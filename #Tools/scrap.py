import json
import sys
import requests
import time
from googlesearch import search
from words import words

url = "http://localhost"
password = "1q2W3e4R%T^Y"

payload = {"pass": password}
headers = {'Content-Type': 'application/json'}

response = requests.request("POST", url + '/login', headers=headers, data = json.dumps(payload))
print(response.text)
token = json.loads(response.text)["data"]["token"]

for i in words[15:]:
  apiurl = url + "/pdf/url"
  headers = {
      'Content-Type': 'application/json',
      'Cookie': 'token=' + token
    }
  #try:
  if True:
    print(search(i + ' filetype:pdf'))
    for ur in search(i + ' filetype:pdf'):

      data =  { "file": ur}
      response = requests.request("POST", apiurl, headers=headers, data = json.dumps(data))
      time.sleep(2);
      print(response)
 # except:
#      time.sleep(1200)
  print(i + " done")
