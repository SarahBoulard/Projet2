# Les import
import csv
import re
import requests

# Les from
from datetime import date
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# En gros, l'étape 2 mais dans une fonction
def extraire_info_livre(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table_data = {row.th.text: row.td.text for row in soup.find_all("tr")}
    number_available = re.search(r"\d+", table_data["Availability"]).group()

    # Dans la cas ou les livres n'ont pas de description
    description = ""
    description_div = soup.find("div", id="product_description")
    if description_div:
        description = description_div.find_next_sibling("p").text

    category = soup.find("ul", class_="breadcrumb").find_all("a")[2].text
    ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    rating_word = soup.find("p", class_="star-rating")["class"][1]
    image_src = soup.find("div", id="product_gallery").find("img")["src"]

    return {
        "product_page_url": url,
        "universal_product_code (upc)": table_data["UPC"],
        "title": soup.find("h1").text,
        "price_including_tax": table_data["Price (incl. tax)"],
        "price_excluding_tax": table_data["Price (excl. tax)"],
        "number_available": number_available,
        "product_description": description,
        "category": category,
        "review_rating": ratings[rating_word],
        "image_url": urljoin(url, image_src),
    }


def get_book_urls(category_url):
    book_urls = []
    page_url = category_url

    # Tant qu'il y a une page à visiter
    while page_url:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Liens des livres de la page (adresses relatives -> complètes)
        for link in soup.select("article.product_pod h3 a"):
            book_urls.append(urljoin(page_url, link["href"]))

        # Lien "next" : s'il existe, on passe à la page suivante, sinon on s'arrête
        next_link = soup.find("li", class_="next")
        if next_link:
            page_url = urljoin(page_url, next_link.find("a")["href"])
        else:
            page_url = None

    return book_urls


category_url = "https://books.toscrape.com/catalogue/category/books/horror_31/index.html"

books = []
for book_url in get_book_urls(category_url):
    books.append(extraire_info_livre(book_url))

# Nom du fichier : catégorie + date, ex. mystery_2026-10-06.csv
category_name = re.sub(r"[^a-zA-Z0-9]+", "_", books[0]["category"]).strip("_").lower()
filename = f"{category_name}_{date.today()}.csv"

with open(filename, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=books[0].keys())
    writer.writeheader()
    writer.writerows(books)

print(f"{len(books)} livres enregistrés dans {filename}")
