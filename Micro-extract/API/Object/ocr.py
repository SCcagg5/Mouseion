import pdftotext
import requests
from .elastic import es

class ocr:
    def download(file):
        file = str(file)
        try:
            url = 'https://nldocuments.s3-eu-west-1.amazonaws.com/FRANCE/' + file
            r = requests.get(url, stream=True)

            with open("./files/" + file, 'wb') as fd:
                for chunk in r.iter_content(2000):
                    fd.write(chunk)
        except:
            return [False, "Invalid File name:" + file, 400]
        return [True, {}, None]


    def analyse(file):
        try:
            with open("./files/" + file , "rb") as f:
                pdf = pdftotext.PDF(f)
            text =  "".join(pdf)
        except:
            return [False, "Invalid pdf file", 400]
        input = {"title": file, "text": text}
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
