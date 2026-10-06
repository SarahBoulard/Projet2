# Les import
import csv
import re
import requests

# Les from
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Récup la page
url = "https://books.toscrape.com/catalogue/sense-and-sensibility_49/index.html"
reponse = requests.get(url)

# ça annalyse la page html
soup = BeautifulSoup(reponse.content, 'html.parser')

title = soup.find("h1").text
table_info = {row.th.text: row.td.text for row in soup.find_all("tr")}

# ça traduit le nombre de livre disponible en chiffre
number_available = re.search(r"\d+", table_info["Availability"]).group()

description = soup.find("div", id="product_description").find_next_sibling("p").text
category = soup.find("ul", class_="breadcrumb").find_all("li")[2].text.strip()
rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
rating_word = soup.find("p", class_="star-rating")["class"][1]
review_rating = rating[rating_word]
image_src = soup.find("div", id="product_gallery").find("img")["src"]
image_url = urljoin(url, image_src)

livre = {
    "url": url,
    "title": title,
    "upc": table_info["UPC"],
    "prix_sans_taxe": table_info["Price (excl. tax)"],
    "prix_avec_taxe": table_info["Price (incl. tax)"],
    "number_available": number_available,
    "description": description,
    "category": category,
    "review_rating": review_rating,
    "image_url": image_url
}


# ça écrit le fichier CSV#
filename = f"{title}.csv"
with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=livre.keys())
    writer.writeheader()
    writer.writerow(livre)

print("CSV créé")

