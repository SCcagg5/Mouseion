import pdftotext
import requests
import os
from .elastic import es
from langdetect import detect
from urllib.parse import urlparse
import re

BASE_URL = str(os.getenv('URL', ''))

class ocr:
    def multiplefiles(files):
        if not isinstance(files, list):
            return [False, "Files should be a list", 400]
        total = {}
        for file in files:
            file = str(file)
            res = ocr.download(file)
            if not res[0]:
                add = {"succes": False, "error": res[1]}
            else:
                res = ocr.analyse(file)
                if not res[0]:
                    add = {"succes": False, "error": res[1]}
                else:
                    add = {"success": True, "data": res[1]}
            total[file] = add
        return [True, total, None]

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


    def download(file):
        file = str(file)
        ext = file.split('.')
        url = urlparse(BASE_URL + file).geturl()
        file = file.split('/')
        file = file[len(file) - 1]
        if ext[len(ext) - 1] != "pdf":
            return [False, "Invalid pdf file", 400]
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
                return [False, "File already in database", 400]
        except:
            es.indices.create(index = 'documents')
        try:
            r = requests.get(url, stream=True)
            with open("./files/" + file, 'wb') as fd:
                for chunk in r.iter_content(2000):
                    fd.write(chunk)
        except:
            return [False, "Invalid File name:" + file, 400]
        return [True, {}, None]


    def analyse(file):
        url = urlparse(BASE_URL + file).geturl()
        file = file.split('/')
        file = file[len(file) - 1]
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
                return [False, "File already in database", 400]
        except:
            es.indices.create(index = 'documents')
        try:
            with open("./files/" + file , "rb") as f:
                pdf = pdftotext.PDF(f)
            text =  "".join(pdf)
            os.remove("./files/" + file)
            if len(text) > 10000:
                return [False, "Text too long", 400]
            lang = detect(text)
        except:
            return [False, "Invalid pdf file", 400]
        input = {"title": file, "text": text, "url": url, "lang": lang}
        try:
            query = { "query": { "match": {
                  "title": {
                    "query" : file,
                    "operator" : "and",
                    "zero_terms_query": "all"
                  }}}}
            es.indices.refresh(index="documents")
            res = es.search(index="documents", body=query)
            if str(res["hits"]["total"]["value"]) == "0":
                res = es.index(index='documents',body=input, request_timeout=30)
            else:
                input = {"title": None, "text": None, "error": "file already in database"}
        except:
            es.indices.create(index = 'documents')
            res = es.index(index='documents',body=input)
        return [True, {"input": input, "text": text}, None]

    def search(word):
        word = str(word)
        regex = word.replace(" ", "\\ ")
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
                                      short limit = """ + str(limit) + """ ;
                                      String[] x = new String[limit];
                                      String[] x2 = new String[limit];
                                      Pattern reg = /.{0,10}\\b""" + regex + """\\b.{0,100}/im;
                                      def m = reg.matcher(params._source.text);
                                      while ( m.find() && i < limit ) {
                                         x[i] = m.group();
                                         ++i;
                                      }
                                      reg = /.{0,10}(\\B""" + regex + """|""" + regex + """\\B|\\B""" + regex + """\\B).{0,100}/im;
                                      m = reg.matcher(params._source.text);
                                      while ( m.find() && i2 < limit ) {
                                          x2[i2] = m.group();
                                          ++i2;
                                      }
                                      String[][] res = new String[2][i > i2 ? i + 1 : i2 + 1];
                                      res[0][0] = Integer.toString(i);
                                      while (--i >= 0) {
                                        res[0][i + 1] = x[i];
                                      }
                                      res[1][0] = Integer.toString(i2);
                                      while (--i2 >= 0) {
                                        res[1][i2 + 1] = x2[i2];
                                      }
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
                    }
                },
            "score": l1 * limit + l2
            }
            for i2 in range(data["match"]["perfect"]["length"]):
                data["match"]["perfect"]["data"][i2] = re.sub(' +', ' ', data["match"]["perfect"]["data"][i2])
            for i2 in range(data["match"]["fuzzy"]["length"]):
                data["match"]["fuzzy"]["data"][i2] = re.sub(' +', ' ', data["match"]["fuzzy"]["data"][i2])
            if data["match"]["fuzzy"]["length"] == 0 and data["match"]["perfect"]["length"] == 0:
                del data["match"]
                sup.append(data)
            else:
                if data["match"]["fuzzy"]["length"] == 0:
                    del data["match"]["fuzzy"]
                if data["match"]["perfect"]["length"] == 0:
                    del data["match"]["perfect"]
                mat.append(data)
        n = len(mat)
        for i in range(n):
            for j in range(0, n-i-1):
                if mat[j]["score"] < mat[j+1]["score"] :
                    mat[j], mat[j+1] = mat[j+1], mat[j]
        return [True, {"matches": mat, "supposed": sup}, None]
