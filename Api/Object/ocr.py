import pdftotext
import requests
import os
from .elastic import es
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

BASE_URL = str(os.getenv('URL', ''))
class pdf:
    def get_title(path, file, title = None):
        if title is None:
            title = PdfReader("./files/" + file).Info.Title
            title = title.strip('()') if title else None
        return [True, {"title": title if title else file.split(".pdf")[0]} , None]

    def get_text(path, file, limit = None):
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
        l = text
        chara = ",'’&/-●"
        for k in chara:
            l = l.replace(k, ' ')
        l = [w for w in l.strip(string.punctuation).split() if len(w)>1]
        map = {"lexiq": ' '.join(list(dict.fromkeys(l))), "count": {}}
        n = 0
        while n < len(l):
            if str(l[n]) not in map["count"]:
                map["count"][str(l[n])] = 1
            else:
                map["count"][str(l[n])] += 1
            n += 1
        return [True, {"text": text, "content": content, "map": map}, None]

    def get_lang(text, lang = None):
        return [True, {"lang" : lang if lang else detect(text)}, None]

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

    def exist(url, date = None):
        try:
            query = { "query": { "match": {
                  "url": {
                    "query" : url,
                    "operator" : "and",
                    "zero_terms_query": "all"
                  }}}}
            es.indices.refresh(index="documents")
            res = es.search(index="documents", body=query)
            if str(res["hits"]["total"]["value"]) != "0":
                if date is None:
                    return True
                elif "date" in res["hits"]["hits"][0]["_source"] :
                   return True if date == res["hits"]["hits"][0]["_source"]["date"] else False
        except:
            es.indices.create(index='documents')
        return False

class ocr:
    def multiplefiles(files):
        if not isinstance(files, list):
            return [False, "Files should be a list", 400]
        total = {}
        for file in files:
            if not isinstance(file, list):
                return [False, "Files should be a list of objects", 400]
            res = ocr.download( str(file["file"]))
            if not res[0]:
                add = {"succes": False, "error": res[1]}
            else:
                res = ocr.analyse(str(file["file"]),
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


    def download(file):
        file = str(file)
        ext = file.split('.')
        url = urlparse(BASE_URL + file).geturl()
        file = file.split('/')
        file = file[len(file) - 1].split('#')[0].split('?')[0]
        try:
            r = requests.get(url, stream=True)
            if "Last-Modified" in r.headers:
                date = r.headers["Last-Modified"]
                if pdf.exist(url, date):
                    return [False, "File in this version already in database", 400]
            else:
                date = None
                if pdf.exist(url):
                    return [False, "File already in database", 400]
            with open("./files/" + file, 'wb') as fd:
                for chunk in r.iter_content(2000):
                    fd.write(chunk)
        except:
            return [False, "Invalid File name:" + file, 400]
        return [True, {"date": date}, None]

    def frombase64(b64, type):
        b64 = str(b64)
        name = b64[:10] + "." + type
        bytes = base64.b64decode(b64)
        url = name
        f = open('./files/' + name , 'wb')
        f.write(bytes)
        f.close()
        if pdf.exist(url):
            return [False, "File already in database", 400]
        return [True, {"url": url, "name": name}, None]



    def pdf_analyse(file, title, lang, restriction, save, url, name, folder, date):
        if restriction and not isinstance(restriction, list):
            return [False, "Restriction should be a list", 400]
        url = url if url else urlparse(BASE_URL + file).geturl()
        if name:
            file = name
        else:
            file = file.split('/')
            file = file[len(file) - 1].split('#')[0].split('?')[0]
        if pdf.exist(url, date):
            return [False, "File already in database", 400]

        input = {"type": "pdf", "url": url}

        input["title"] = pdf.get_title("./files/", file, title)[1]["title"]
        input["restriction"] = str(pdf.get_restriction(restriction)[1]["restriction"])
        if folder:
            input["folder"] = folder
        if date:
            input["date"] = date
        text = pdf.get_text("./files/", file)
        if text[0]:
             if save:
                input["content"] = text[1]["content"]
             input["text"] = text[1]["text"]
             input["map"] = text[1]["map"]
        input["lang"] = pdf.get_lang(input["text"] if 'text' in input else None, lang)[1]["lang"]
        try:
            res = es.index(index='documents', body=input, request_timeout=30)
        except:
            es.indices.create(index = 'documents')
            res = es.index(index='documents', body=input, request_timeout=30)
        return [True, {"input": input}, None]

    def img_analyse(file, title, lang, restriction, save, url, name, folder, date):
        if restriction and not isinstance(restriction, list):
            return [False, "Restriction should be a list", 400]
        url = url if url else urlparse(BASE_URL + file).geturl()
        if name:
            file = name
        else:
            file = file.split('/')
            file = file[len(file) - 1].split('#')[0].split('?')[0]
        if pdf.exist(url, date):
            return [False, "File already in database", 400]

        input = {"type": "img", "url": url}

        input["title"] = title
        input["restriction"] = str(pdf.get_restriction(restriction)[1]["restriction"])
        if folder:
            input["folder"] = folder
        if date:
            input["date"] = date
        text = image_to_string(Image.open("./files/" + file))
        if text:
             input["text"] = text
        input["lang"] = pdf.get_lang(str(text), lang)[1]["lang"]
        try:
            res = es.index(index='documents', body=input, request_timeout=30)
        except:
            es.indices.create(index = 'documents')
            res = es.index(index='documents', body=input, request_timeout=30)
        return [True, {"input": input}, None]

    def file_analyse(file, title, lang, restriction, save, url, name, folder, date):
        if restriction and not isinstance(restriction, list):
            return [False, "Restriction should be a list", 400]
        url = url if url else urlparse(BASE_URL + file).geturl()
        if name:
            file = name
        else:
            file = file.split('/')
            file = file[len(file) - 1].split('#')[0].split('?')[0]
        if pdf.exist(url, date):
            return [False, "File already in database", 400]

        input = {"type": "file", "url": url}

        input["title"] = title
        input["restriction"] = str(pdf.get_restriction(restriction)[1]["restriction"])
        if folder:
            input["folder"] = folder
        if date:
            input["date"] = date
        input["lang"] = pdf.get_lang("", lang)[1]["lang"]
        try:
            res = es.index(index='documents', body=input, request_timeout=30)
        except:
            es.indices.create(index = 'documents')
            res = es.index(index='documents', body=input, request_timeout=30)
        return [True, {"input": input}, None]

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
            es.indices.refresh(index="documents")
            res = es.search(index="documents", body=query)
            if str(res["hits"]["total"]["value"]) == "0":
                return [False, "No such file", 404]
            else:
                text = res["hits"]["hits"][0]["_source"]
        except:
            es.indices.create(index = 'documents')
            return [False, "Internal Error", 500]
        return [True, {"text": text}, None]

    def search(word, lang, type, date_from, date_to, full = None):
        word = unidecode.unidecode(str(word)) if word else ""
        regex = word.replace(" ", "\\ ").replace("e", "[eéèêë]").replace("a", "[aàâá]").replace("c", "[cç]").replace("i", "[iïî]").replace("o", "[oòóôö]").replace("u", "[uúùû]")
        limit = 20
        query = {
          "size": 50,
          "_source":["type", "url", "title", "lang"],
          "query": {
            "function_score": {
                "query": {
                     "bool": {
                      "should": [
                        {
                          "multi_match" : {
                            "query":      word,
                            "fields":     ["url", "title", "text"],
                            "type":       "bool_prefix",
                            "boost": 1,
                            "operator": "OR",
                            "slop": 0,
                            "prefix_length": 0,
                            "max_expansions": 50,
                            "zero_terms_query": "NONE",
                            "auto_generate_synonyms_phrase_query": True,
                            "fuzzy_transpositions": True,
                            "tie_breaker": 1
                          }
                        }
                      ]
                    }
                },
                "script_score" : {
                    "script" : {
                      "lang": "painless",
                     "source": """
                                      long i = 0;
                                      String ma;
                                      def m;
                                      Pattern reg1 = /\w{0,20}""" + regex + """\w{0,10}/im;
                                      if (params._source.map != null){
                                          m = reg1.matcher(params._source.map.lexiq);
                                          while (m.find()) {
                                             ma = m.group();
                                             if (params._source.map.count[ma] != null)
                                               i += params._source.map.count[ma];
                                          }
                                          if  (params._source.map.count[""" + '"' + word + '"' + """] != null)
                                             i += params._source.map.count[""" + '"' + word + '"' + """] * 5;
                                      }

                                      reg1 = /""" + regex + """/im;
                                      m = reg1.matcher(params._source.title);
                                      while (m.find()) {
                                        i += 100;
                                      }
                                      m = reg1.matcher(params._source.url);
                                      while (m.find()) {
                                        i += 50;
                                      }
                                      if (params._source.lang != "fr"){
                                        i = i / 5;
                                      }
                                      return i;
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
                                      short i = 0;
                                      short limit = """ + str(limit) + """ ;
                                      String[] x = new String[limit + 1];
                                      if (params._source.text != null){
                                        Pattern reg1 = /(\w{0,20}){0,1}\W{0,3}""" + regex + """(\W{0,3}\w{0,20}){0,4}/im;
                                        def m = reg1.matcher(params._source.text);
                                        while (m.find() && i < limit) {
                                           x[i] = m.group();
                                           ++i;
                                        }
                                        while (m.find()) {
                                           ++i;
                                        }
                                      }
                                      x[limit] = Integer.toString(i);
                                      return x;"""
                   }
                 }
          }
        }
        es.indices.refresh(index="documents")
        res = es.search(index="documents", body=query)["hits"]["hits"]
        ret = []
        i = 0
        while i < len(res):
            i2 = 0
            input = res[i]["_source"]
            match = res[i]["fields"]["match"][0]
            input["score"] = res[i]["_score"]
            input["match"] = {"number": match[limit], "text": []}
            while i2 < limit and match[i2] != None:
                input["match"]["text"].append(match[i2])
                i2 += 1
            ret.append(input)
            i += 1
        return [True, {"result": ret}, None]
