import pdftotext
import requests
from .elastic import es

class ocr:
    def download(file):
        url = 'https://nldocuments.s3-eu-west-1.amazonaws.com/FRANCE/' + file
        r = requests.get(url, stream=True)

        with open("./files/" + file, 'wb') as fd:
            for chunk in r.iter_content(2000):
                fd.write(chunk)
        return [True, {}, None]


    def analyse(file):
        with open("./files/" + file , "rb") as f:
            pdf = pdftotext.PDF(f)
        text =  "".join(pdf)
        input = {"title": file, "text": text}
        try:
            res = es.index(index='documents',body=input)
        except:
            es.indices.create(index = 'documents')
            res = es.index(index='documents',body=input)
        return [True, {"input": input}, None]
