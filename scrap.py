from googlesearch import search
for i in "qwertyuiopasdfghjklzxcvbnm":
  for url in search(i + ' filetype:pdf', stop=100):
    print(url)
