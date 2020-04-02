import pdftotext
import requests
import os
from .elastic import es
from langdetect import detect
from urllib.parse import urlparse

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


    def download(file):
        file = str(file)
        ext = file.split('.')
        if ext[len(ext) - 1] != "pdf":
            return [False, "Invalid pdf file", 400]
        try:
            url = BASE_URL + file
            r = requests.get(urlparse(url).geturl(), stream=True)


            file = file.split('/')
            file = file[len(file) - 1]
            with open("./files/" + file, 'wb') as fd:
                for chunk in r.iter_content(2000):
                    fd.write(chunk)
        except:
            return [False, "Invalid File name:" + file, 400]
        return [True, {}, None]


    def analyse(file):
        url = BASE_URL + file
        file = file.split('/')
        file = file[len(file) - 1]
        try:
            query = { "query": { "match": {
                  "title": {
                    "query" : file,
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
                res = es.index(index='documents',body=input)
            else:
                input = {"title": None, "text": None, "error": "file already in database"}
        except:
            es.indices.create(index = 'documents')
            res = es.index(index='documents',body=input)
        return [True, {"input": input, "text": text}, None]

    def search(word):
        word = str(word)
        query = {
               "query":{
                  "bool":{
                     "must":[
                        {
                          "query_string" : {
                              "query" : "/.*" + word +".*/",
                              "default_field" : "text"
                          }
                        }
                     ]
                  }
               },
              "script_fields": {
                 "match": {
                   "script": {
                     "lang": "painless",
                     "source": """    short i =0;
                                      String[] x = new String[100];
                                      Pattern reg = /.{0,10}""" + word + """.{0,100}/im;
                                      def m = reg.matcher(params._source.text);
                                      while ( m.find() && i < 100 ) {
                                         x[i] = m.group();
                                         ++i;
                                      }
                                      String[] res = new String[i + 1];
                                      res[0] = Integer.toString(i);
                                      while(--i >= 0){
                                        res[i + 1] = x[i];
                                      }
                                      return res;

                                    """
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
               "size":-1
            }
        es.indices.refresh(index="documents")
        res = es.search(index="documents", body=query)
        ret = []
        for i in res["hits"]["hits"]:
            data = {
            "title" : i["fields"]["title"][0],
            "url": i["fields"]["url"][0],
            "lang": i["fields"]["lang"][0],
            "match" : {
                "data" : i["fields"]["match"][0][1:],
                "length": int(i["fields"]["match"][0][0])
                }
            }
            ret.append(data)
        n = len(ret)
        for i in range(n):
            for j in range(0, n-i-1):
                if ret[j]["match"]["length"] < ret[j+1]["match"]["length"] :
                    ret[j], ret[j+1] = ret[j+1], ret[j]
        return [True, {"matches": ret}, None]
