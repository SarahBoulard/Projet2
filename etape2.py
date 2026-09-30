import requests
url = "https://books.toscrape.com/catalogue/sense-and-sensibility_49/index.html"
reponse = requests.get(url)

print(reponse.text)