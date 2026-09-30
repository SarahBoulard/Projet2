import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/catalogue/sense-and-sensibility_49/index.html"
reponse = requests.get(url)
soup = BeautifulSoup(reponse.content, 'html.parser')

upc = soup.find("th", string="UPC").find_next_sibling("td").text
prix_sans_taxe = soup.find("th", string="Price (excl. tax)").find_next_sibling("td").text
prix_avec_taxe = soup.find("th", string="Price (incl. tax)").find_next_sibling("td").text

h1 = soup.find('h1')
print(h1.text, upc, prix_sans_taxe, prix_avec_taxe)