from googlesearch import search
import json

for i in "qwertyuiopasdfghjklzxcvbnm":
  urls = []
  for url in search(i + ' filetype:pdf', stop=100):
    urls.append(url)
  print(json.dumps(urls))
