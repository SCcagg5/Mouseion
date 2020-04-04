from googlesearch import search
import json, sys

urls = []
print(sys.argv[1])
for url in search(sys.argv[1] + ' filetype:pdf', stop=500):
  urls.append(url)
print(json.dumps(urls))
