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
        return [True, {"text": text, "content": content}, None]

    def get_lang(text, lang = None):
        return [True, {"lang" : lang if lang else detect(text)}, None]

    def get_restriction(restriction):
        ret = []
        if restriction is None:
            restriction = []
        for i in restriction:
            ret.append(str(hashlib.sha224(str(restriction).encode()).hexdigest()))
        if len(ret) == 0:
            ret.append(str(hashlib.sha224("public".encode()).hexdigest()))
        return [True, {"restriction": ret}, None]

    def exist(url):
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
                return True
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
                                 str(file["restriction"]) if "restriction" in file else None
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
        file = file[len(file) - 1]
        if ext[len(ext) - 1] != "pdf":
            return [False, "Invalid pdf file", 400]
        if pdf.exist(url):
            return [False, "File already in database", 400]
        try:
            r = requests.get(url, stream=True)
            with open("./files/" + file, 'wb') as fd:
                for chunk in r.iter_content(2000):
                    fd.write(chunk)
        except:
            return [False, "Invalid File name:" + file, 400]
        return [True, {}, None]

    def frombase64(b64):
        b64 = str(b64)
        name = b64[:10] + ".pdf"
        bytes = base64.b64decode(b64)
        url = name
        f = open('./files/' + name , 'wb')
        f.write(bytes)
        f.close()
        if pdf.exist(url):
            return [False, "File already in database", 400]
        return [True, {"url": url, "name": name}, None]

    def analyse(file, title, lang, restriction, save, url, name):
        if restriction and not isinstance(restriction, list):
            return [False, "Restriction should be a list", 400]
        url = url if url else urlparse(BASE_URL + file).geturl()
        if name:
            file = name
        else:
            file = file.split('/')
            file = file[len(file) - 1]
        if pdf.exist(url):
            return [False, "File already in database", 400]
        title = pdf.get_title("./files/", file, title)[1]["title"]
        text = pdf.get_text("./files/", file)
        if not text[0]:
            return text
        content = text[1]["content"] if save else ""
        text = text[1]["text"]
        lang = pdf.get_lang(text, lang)[1]["lang"]
        restriction = pdf.get_restriction(restriction)[1]["restriction"]
        input = {"title": title, "text": text, "base64": content, "url": url, "lang": lang, "restriction": restriction}
        try:
            res = es.index(index='documents',body=input, request_timeout=30)
        except:
            es.indices.create(index = 'documents')
            res = es.index(index='documents',body=input)
        return [True, {"input": input}, None]

    def gettext(url):
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

    def search(word):
        word = unidecode.unidecode(str(word))
        regex = word.replace(" ", "\\ ").replace("e", "[eéèêë]").replace("a", "[aàâá]").replace("c", "[cç]").replace("i", "[iïî]").replace("o", "[oòóôö]").replace("u", "[uúùû]")
        limit = 20
        query = {
               "query":{
                  "bool":{
                    "should": [
                        {
                          "match" : {
                                  "text" : {
                                       "query" : "\"" + word + "\"",
                                       "operator" : "and",
                                       "boost": 2
                                       }
                                    }
                        },
                        {
                          "query_string" : {
                                  "query" : "/.*" + regex +".*/",
                                  "default_field" : "text"
                                          }
                        },
                        {
                          "match" : {
                                  "text" : {
                                       "query" : "\"" + word +"\"",
                                       "operator" : "or"
                                       }
                                    }
                        }
                      ]
                  }
               },
              "script_fields": {
                 "match": {
                   "script": {
                     "lang": "painless",
                     "source": """    short i = 0;
                                      short i2 = 0;
                                      short i3 = 0;
                                      short i4 = 0;
                                      short limit = """ + str(limit) + """ ;
                                      String[] x = new String[limit];
                                      String[] x2 = new String[limit];
                                      Pattern reg1 = /.{0,10}\\b""" + regex + """\\b.{0,100}/im;
                                      Pattern reg2 = /.{0,10}(\\B""" + regex + """|""" + regex + """\\B|\\B""" + regex + """\\B).{0,100}/im;

                                      def m = reg1.matcher(params._source.text);
                                      while ( m.find() && i < limit ) {
                                         x[i] = m.group();
                                         ++i;
                                      }

                                      m = reg2.matcher(params._source.text);
                                      while ( m.find() && i2 < limit ) {
                                          x2[i2] = m.group();
                                          ++i2;
                                      }

                                      m = reg1.matcher(params._source.title);
                                      while ( m.find() && i3 < limit ) {
                                         ++i3;
                                      }

                                      m = reg2.matcher(params._source.title);
                                      while ( m.find() && i4 < limit ) {
                                          ++i4;
                                      }


                                      String[][] res = new String[3][i > i2 ? i + 2 : i2 + 2];

                                      res[0][0] = Integer.toString(i);
                                      while (--i >= 0) {
                                        res[0][i + 1] = x[i];
                                      }

                                      res[1][0] = Integer.toString(i2);
                                      while (--i2 >= 0) {
                                        res[1][i2 + 1] = x2[i2];
                                      }

                                      res[2][0] = Integer.toString(i3);
                                      res[2][1] = Integer.toString(i4);

                                      return res;"""
                   }
                 },
                "title": {
                   "script": {
                     "lang": "painless",
                     "source": "return params._source.title"
                   }
                 },
                "lang": {
                   "script": {
                     "lang": "painless",
                     "source": "return params._source.lang"
                   }
                 },
                 "url": {
                    "script": {
                      "lang": "painless",
                      "source": "return params._source.url"
                    }
                  }
              },
               "size": limit
        }
        es.indices.refresh(index="documents")
        res = es.search(index="documents", body=query)
        mat = []
        sup = []
        for i in res["hits"]["hits"]:
            l1 = int(i["fields"]["match"][0][0][0])
            l2 = int(i["fields"]["match"][0][1][0])
            l3 = int(i["fields"]["match"][0][2][0])
            l4 = int(i["fields"]["match"][0][2][1])
            data = {
            "title" : i["fields"]["title"][0],
            "url": i["fields"]["url"][0],
            "lang": i["fields"]["lang"][0],
            "match" : {
                "perfect": {
                        "data" : i["fields"]["match"][0][0][1:l1 + 1],
                        "length": l1,
                    },
                "fuzzy": {
                        "data" : i["fields"]["match"][0][1][1:l2 + 1],
                        "length": l2,
                    },
                "title": l3 + l4
                },
            "score": l1 * limit + l2 + l3 * limit * limit + l4 * limit
            }
            for i2 in range(data["match"]["perfect"]["length"]):
                data["match"]["perfect"]["data"][i2] = re.sub(' +', ' ', data["match"]["perfect"]["data"][i2])
            for i2 in range(data["match"]["fuzzy"]["length"]):
                data["match"]["fuzzy"]["data"][i2] = re.sub(' +', ' ', data["match"]["fuzzy"]["data"][i2])
            if data["match"]["fuzzy"]["length"] == 0 and data["match"]["perfect"]["length"] == 0 and data["match"]["title"] == 0:
                del data["match"]
                sup.append(data)
            else:
                if data["match"]["fuzzy"]["length"] == 0:
                    del data["match"]["fuzzy"]
                if data["match"]["perfect"]["length"] == 0:
                    del data["match"]["perfect"]
                if data["match"]["title"] == 0:
                    del data["match"]["title"]
                mat.append(data)
        n = len(mat)
        for i in range(n):
            for j in range(0, n-i-1):
                if mat[j]["score"] < mat[j+1]["score"] :
                    mat[j], mat[j+1] = mat[j+1], mat[j]
        return [True, {"matches": mat, "supposed": sup, "query": query}, None]
