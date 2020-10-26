import pdftotext
import requests
import os
from .elastic import es, mapping
from langdetect import detect
from urllib.parse import urlparse
from pdfrw import PdfReader
import unidecode
import re
import base64
import hashlib
from PIL import Image
from pytesseract import image_to_string
import string
from datetime import date

class pdf:
    def get_title(path, file, title = None):
        if title is None:
            title = PdfReader("./files/" + file).Info.Title
            title = title.strip('()') if title else None
        return [True, {"title": title if title else file.split(".pdf")[0]} , None]

    def get_text(path, file, limit = 800000):
        try:
            with open(path + file , "rb") as f:
                p = pdftotext.PDF(f)
            text =  "".join(p)
            if limit:
                if len(text) > limit:
                    return [False, "Text too long", 400]
            content = base64.encodestring(open(path + file , "rb").read()).decode("utf-8").replace("\n", "")
        except:
            return [False, "Invalid pdf", 400]
        l = text.lower()
        chara = ",'’&/-●“”()‘…;\"[]{}<>_&^+=|\\:"
        for k in chara:
            l = l.replace(k, ' ')
        l = l.replace('. ', ' ')
        l = l.replace('.\n', ' ')
        l = l.replace('.\t', ' ')
        max = 50
        t = l.strip(string.punctuation).split()
        le = [w for w in  t if len(w) > 3]
        map = {"lexiq": ' '.join(list(dict.fromkeys(le))), "count": {}}
        n = 0
        while n < len(le):
            if str(le[n]) not in map["count"]:
                map["count"][str(le[n])] = 1
            else:
                map["count"][str(le[n])] += 1
            n += 1
        limit_l = 1
        while len(map["count"]) > max:
            t = []
            for i in map["count"]:
                if map["count"][i] <= limit_l and len(map["count"]) - len(t) > max :
                    t.append(i)
            for i in t:
                del map["count"][i]
            limit_l += 1
        return [True, {"text": text, "content": content, "map": map["count"], "lexiq": map["lexiq"]}, None]

class ged:
    def multiplefiles(files):
        if not isinstance(files, list):
            return [False, "Files should be a list", 400]
        total = {}
        for file in files:
            if not isinstance(file, dict):
                return [False, "Files should be a list of objects", 400]
            res = ged.download( str(file["file"]))
            if not res[0]:
                add = {"succes": False, "error": res[1]}
            else:
                res = ocr.pdf_analyse(str(file["file"]),
                                     str(file["title"]) if "title" in file else None,
                                     str(file["lang"]) if "lang" in file else None,
                                     str(file["restriction"]) if "restriction" in file else None,
                                     str(file["save"]) if "save" in file else None,
                                     None,
                                     None,
                                     str(file["folder"]) if "folder" in file else None,
                                     str(res[1]["date"])
                                     )
                if not res[0]:
                    add = {"succes": False, "error": res[1]}
                else:
                        add = {"success": True, "data": res[1]}
            total[str(file["file"])] = add
        return [True, total, None]

    def download(f):
        f = str(f)
        ext = f.split('.')
        url = urlparse(f).geturl()
        f = f.split('/')
        f = f[len(f) - 1].split('#')[0].split('?')[0]
        try:
        #if True:
            r = requests.get(url, stream=True)
            if "Last-Modified" in r.headers:
                date = r.headers["Last-Modified"]
                if file.exist(url, date):
                    return [False, "File in this version already in database", 400]
            else:
                date = None
                if file.exist(url):
                    return [False, "File already in database", 400]
            with open("./files/" + f, 'wb') as fd:
                for chunk in r.iter_content(2000):
                    fd.write(chunk)
        except:
            return [False, "Invalid File name:" + file, 400]
        return [True, {"date": date}, None]

    def get_restriction(restriction, public = False):
        ret = []
        if restriction is None:
            restriction = ["public"]
        elif public is True:
            restriction.append("public")
        for i in restriction:
            if i == "public":
                ret.append([0, str(hashlib.sha224("public".encode()).hexdigest())])
            else:
                ret.append([1, str(hashlib.sha224(str(i).encode()).hexdigest())])
        return [True, {"restriction": ret}, None]

    def index():
        id = "ged_doc_" + date.today().strftime("%Y%m%d")
        if es.indices.exists(index=id):
            es.indices.refresh(index=id)
        else:
            es.indices.create(index=id, body=mapping)
        return id

class file:
    def exist(url, date = None):
        try:
            query = { "query": { "match": {
                        "url": {
                        "query" : url,
                        "operator" : "and",
                        "zero_terms_query": "all"
                     }}}}
            ged.index()
            res = es.search(index=ged.index(), body=query)
            if str(res["hits"]["total"]["value"]) != "0":
                if date is None:
                    return True
                elif "date" in res["hits"]["hits"][0]["_source"] :
                   return True if date == res["hits"]["hits"][0]["_source"]["date"] else False
        except:
              pass
        return False

    def get_lang(text, lang = None):
        return [True, {"lang" : lang if lang else detect(text)}, None]

    def gettext(url, date):
        text = ""
        url = str(url)
        try:
            query = { "query": { "match": {
                  "url": {
                    "query" : url,
                    "operator" : "and",
                    "zero_terms_query": "all"
                  }}}}
            index_template = "ged_doc_" + date.today().strftime("%Y%m%d")
            ged.index()
            res = es.search(index=re.findall(r''+index_template+'[0-9]*', es.cat.indices()),
                            body=query)
            if str(res["hits"]["total"]["value"]) == "0":
                return [False, "No such file", 404]
            else:
                text = res["hits"]["hits"][0]["_source"]
        except:
            ged.index()
            return [False, "Internal Error", 500]
        return [True, {"text": text}, None]

    def simplify(word):
        return word.replace('\\', '\\\\').replace(" ", "\\ ").replace('.', '\\.').replace('@', '.').replace("e", "[eéèêë]").replace("a", "[aàâá]").replace("c", "[cç]").replace("i", "[iïî]").replace("o", "[oòóôö]").replace("u", "[uúùû]")

    def search(word, lang, type, date_from, date_to, page = 1, size = 20):
        word = unidecode.unidecode(str(word)) if word else ""
        regex = file.simplify(word)
        words = sorted(word.split(" "), key=len)[::-1]
        regexs = [file.simplify(i) for i in words]
        limit = 6
        page = 1 if page is None or int(page) < 2 else int(page)
        size = 20 if size is None or int(size) < 20 else int(size)
        query = {
          "size": size,
          "from" : (page - 1)  * size,
          "_source":["type", "url", "title", "lang", "date"],
          "query": {
            "function_score": {
                "query": {
                     "bool": {
                      "should": [
                        {
                            "match": {
                                "text": {
                                    "query": word
                                }
                            }
                        }for word in words ] + [
                        {
                            "regexp": {
                                "lexiq": {
                                    "value": word
                                }
                            }
                        }for word in words ] + [
                        {
                            "regexp": {
                                "lexiq": {
                                    "value": f".*{regex}.*"
                                }
                            }
                        }for regex in regexs ] + [
                        {
                          "regexp": {
                            "url": {
                                "value":  regex,
                                "max_determinized_states": 100,
                                "rewrite": "constant_score",
                                "flags": "ALL"
                            }
                          }
                        } for regex in regexs ]
                    }
                },
                "script_score" : {
                    "script" : {
                        "lang": "painless",
                        "source": f"""
                                   int i = 1;
                                   int i2 = 1;
                                   int i3 = 0;
                                   String ma;
                                   def m;
                                   Pattern reg1;
                                   """ +
                                   "".join([f"""
                                   reg1 = /{regexs[i]}/im;
                                   if (params._source.lexiq != null){{
                                      i3 = 0;
                                      m = reg1.matcher(params._source.lexiq);
                                      while (m.find()) {{
                                         ma = m.group();
                                         if (params._source.map[ma] != null) {{
                                            i += params._source.map[ma];
                                         }} else {{
                                            ++i;
                                         }}
                                         if (i3 == 0){{
                                            i2 = i2 + {len(words[1]) / 4 if len(words) > 4 else 1};
                                            i3 = 1;
                                         }}
                                      }}
                                      if  (params._source.map[\"{words[i]}\"] != null) {{
                                         i += params._source.map[\"{words[i]}\"] * 10 * i;
                                      }}
                                   }}
                                   m = reg1.matcher(params._source.title);
                                   while (m.find()) {{
                                      i += 1000;
                                   }}
                                   m = reg1.matcher(params._source.url);
                                   while (m.find()) {{
                                      i += 500;
                                   }}
                                   """ for i in range(len(words))]) + f"""
                                   if (params._source.lang != \"{lang}\") {{
                                      i /= 100;
                                   }}
                                   return (i * i2 * i2 );
                                  """
                   }
                }
            }}
           ,
          "script_fields": {
                 "match": {
                   "script": {
                     "lang": "painless",
                     "source": """
                                short i1 = 0;
                                short i2 = 0;
                                short limit = """ + str(limit) + """ ;
                                String[] x = new String[limit + 2];
                                def m;
                                Pattern reg1;
                                if (params._source.text != null) {
                                    reg1 = /(\w{0,20}){0,1}\W{1,3}""" + regex +"""\W{1,3}(\W{0,3}\w{0,20}){0,4}/im;
                                    m = reg1.matcher(params._source.text);
                                    while (m.find() && i1 + i2 < limit) {
                                        x[i1] = m.group();
                                        ++i1;

                                    }
                                    while (m.find()) {
                                        ++i1;
                                    }
                                """ + "if (i1 == 0) {"+
                                "".join([
                                    """
                                        reg1 = /(\w{0,20}){0,1}\W{1,3}""" + regex +"""\W{1,3}(\W{0,3}\w{0,20}){0,4}/im;
                                        m = reg1.matcher(params._source.text);
                                        while (m.find() && i1 + i2 < limit) {
                                            x[i1] = m.group();
                                            ++i1;

                                        }
                                        while (m.find()) {
                                            ++i2;
                                        }
                                    """
                                for regex in regexs ]) + "} "+ "".join([
                                    """
                                        reg1 = /(\w{0,20}){0,1}\W{0,3}""" + regex +"""(\W{0,3}\w{0,20}){0,4}/im;
                                        m = reg1.matcher(params._source.text);
                                        while (m.find() && i1 + i2 < limit) {
                                            x[i1 + i2] = m.group();
                                            ++i2;
                                        }
                                        while (m.find()) {
                                            ++i2;
                                        }
                                    """ for regex in regexs ]) +
                                """
                                }
                                x[limit] = Integer.toString(i1);
                                x[limit + 1] = Integer.toString(i2);
                                return (x);
                               """
                   }
                 }
          }
        }
        index_template = "ged_doc_"
        ged.index()
        res = es.search(index=re.findall(r''+index_template+'[0-9]*', es.cat.indices()),
                        body=query,
                        request_timeout=600)["hits"]["hits"]
        ret = []
        pos = []
        i = 0
        while i < len(res):
            i2 = 0
            input = res[i]["_source"]
            match = res[i]["fields"]["match"][0]
            input["score"] = res[i]["_score"]
            input["match"] = {"perfect": int(match[limit]), "partial":  int(match[limit + 1]) , "text": []}
            while i2 < limit and match[i2] != None:
                input["match"]["text"].append(match[i2].strip())
                i2 += 1
            input["match"]["text"] = list(dict.fromkeys(input["match"]["text"]))
            if lang == input["lang"]:
              if input["match"]["perfect"] == 0 and input["match"]["partial"] == 0:
                  del input["match"]
                  if re.compile(r'.*' +regex+'.*', flags=re.IGNORECASE).search(str(input['title'])) is not None:
                    ret.append(input)
                  else:
                    pos.append(input)
              else:
                  ret.append(input)
            i += 1
        return [True, {"result": ret, "possible": pos}, None]



class ocr:
    def frombase64(b64, type):
        b64 = str(b64)
        name = b64[:10] + "." + type
        bytes = base64.b64decode(b64)
        url = name
        f = open('./files/' + name , 'wb')
        f.write(bytes)
        f.close()
        if file.exist(url):
            return [False, "File already in database", 400]
        return [True, {"url": url, "name": name}, None]



    def pdf_analyse(f, title, lang, restriction, save, url, name, folder, date):
        if restriction and not isinstance(restriction, list):
            return [False, "Restriction should be a list", 400]
        url = url if url else urlparse(f).geturl()
        if name:
            f = name
        else:
            f = f.split('/')
            f = f[len(f) - 1].split('#')[0].split('?')[0]
        if file.exist(url, date):
            return [False, "File already in database", 400]
        input = {"type": "pdf", "url": url}
        input["title"] = pdf.get_title("./files/", f, title)[1]["title"]
        input["restriction"] = str(ged.get_restriction(restriction)[1]["restriction"])
        if folder:
            input["folder"] = folder
        if date:
            input["date"] = date
        text = pdf.get_text("./files/", f)
        if text[0]:
             if save:
                input["content"] = text[1]["content"]
             input["text"] = text[1]["text"]
             input["map"] = text[1]["map"]
             input["lexiq"] = text[1]["lexiq"]
        input["lang"] = file.get_lang(input["text"] if 'text' in input else None, lang)[1]["lang"]
        res = es.index(index=ged.index(), body=input, request_timeout=30)
        return [True, {"input": input}, None]

    def img_analyse(f, title, lang, restriction, save, url, name, folder, date):
        if restriction and not isinstance(restriction, list):
            return [False, "Restriction should be a list", 400]
        url = url if url else urlparse(f).geturl()
        if name:
            f = name
        else:
            f = f.split('/')
            f = f[len(f) - 1].split('#')[0].split('?')[0]
        if file.exist(url, date):
            return [False, "File already in database", 400]

        input = {"type": "img", "url": url}
        input["title"] = title
        input["restriction"] = str(ged.get_restriction(restriction)[1]["restriction"])
        if folder:
            input["folder"] = folder
        if date:
            input["date"] = date
        text = image_to_string(Image.open("./files/" + f))
        if text:
             input["text"] = text
        input["lang"] = f.get_lang(str(text), lang)[1]["lang"]
        try:
            res = es.index(index=ged.index(), body=input, request_timeout=30)
        except:
            return [False, "unkown error", 500]
        return [True, {"input": input}, None]

    def file_analyse(f, title, lang, restriction, save, url, name, folder, date):
        if restriction and not isinstance(restriction, list):
            return [False, "Restriction should be a list", 400]
        url = url if url else urlparse(f).geturl()
        if name:
            f = name
        else:
            f = f.split('/')
            f = f[len(f) - 1].split('#')[0].split('?')[0]
        if file.exist(url, date):
            return [False, "File already in database", 400]

        input = {"type": "file", "url": url}

        input["title"] = title
        input["restriction"] = str(ged.get_restriction(restriction)[1]["restriction"])
        if folder:
            input["folder"] = folder
        if date:
            input["date"] = date
        input["lang"] = file.get_lang("", lang)[1]["lang"]
        try:
            res = es.index(index=ged.index(), body=input, request_timeout=30)
        except:
            return [False, "", 500]
        return [True, {"input": input}, None]
