"""Scrapeur de livres pour books.toscrape.com.

Ce script parcourt les catégories du site, récupère les informations de chaque
livre, télécharge leurs couvertures et enregistre le résultat dans des fichiers
CSV dans le dossier "donnees".
"""

import csv
import os
import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# -------------------------------
# Fonctions utilitaires
# -------------------------------
def clean_name(text):
    # Permet d'obtenir un nom de fichier ou de dossier compatible avec le système.
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()


def download_image(image_url, category, title):
    # Télécharge une image dans un sous-dossier correspondant à la catégorie.
    folder = os.path.join("donnees", "images", clean_name(category))
    os.makedirs(folder, exist_ok=True)

    # On garde l'extension d'origine pour conserver le bon format d'image.
    extension = os.path.splitext(image_url)[1]
    image_name = clean_name(title)
    image_path = os.path.join(folder, f"{image_name}{extension}")

    response = requests.get(image_url)
    with open(image_path, "wb") as image_file:
        image_file.write(response.content)


# -------------------------------
# Extraction des données
# -------------------------------
def extract_book_data(url):
    # Récupère les informations complètes d'un livre à partir de sa page produit.
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # On transforme les lignes du tableau "Product Information" en dictionnaire.
    table = {
        row.th.text: row.td.text
        for row in soup.find_all("tr")
    }

    # La disponibilité est indiquée comme "In stock (20 available)" ; on n'extrait que le nombre.
    available_quantity = re.search(r"\d+", table["Availability"]).group()

    # Certaines fiches ne contiennent pas de description.
    description = ""
    description_div = soup.find("div", id="product_description")

    if description_div:
        description = description_div.find_next_sibling("p").text

    # La catégorie est la troisième entrée du fil d'Ariane (Home > Category > Book).
    category = soup.find("ul", class_="breadcrumb").find_all("a")[2].text

    # Les étoiles sont codées par un texte de type "One", "Two", etc.
    ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    rating_name = soup.find("p", class_="star-rating")["class"][1]

    # L'image peut être fournie avec une URL relative : on la convertit en URL absolue.
    image_source = soup.find("div", id="product_gallery").find("img")["src"]
    image_url = urljoin(url, image_source)
    title = soup.find("h1").text.strip()

    # On télécharge immédiatement la couverture du livre pour la stocker localement.
    download_image(image_url, category, title)

    # Les clés de ce dictionnaire correspondent aux colonnes du CSV final.
    return {
        "product_page_url": url,
        "universal_product_code (upc)": table["UPC"],
        "title": title,
        "price_including_tax": table["Price (incl. tax)"],
        "price_excluding_tax": table["Price (excl. tax)"],
        "number_available": available_quantity,
        "product_description": description,
        "category": category,
        "review_rating": ratings[rating_name],
        "image_url": image_url,
    }


def get_book_urls(category_url):
    # Renvoie tous les liens vers les livres d'une catégorie, y compris sur plusieurs pages.
    book_urls = []
    page_url = category_url

    while page_url:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            book_urls.append(urljoin(page_url, link["href"]))

        # Si une page contient un bouton "next", on continue la pagination.
        next_link = soup.find("li", class_="next")

        if next_link:
            page_url = urljoin(page_url, next_link.find("a")["href"])
        else:
            page_url = None

    return book_urls


def get_categories(homepage_url):
    # Récupère la liste des catégories présentes dans la barre latérale du site.
    response = requests.get(homepage_url)
    soup = BeautifulSoup(response.content, "html.parser")

    categories = {}

    # On sélectionne les liens de navigation qui mènent vers les catégories.
    for link in soup.select("div.side_categories ul li ul li a"):
        categories[link.text.strip()] = urljoin(homepage_url, link["href"])

    return categories


# -------------------------------
# Point d'entrée du script
# -------------------------------
homepage_url = "https://books.toscrape.com/index.html"

# Le dossier "donnees" est créé au lancement pour stocker les exports et les images.
os.makedirs("donnees", exist_ok=True)

# On boucle sur chaque catégorie, récupère ses livres, puis exporte les données dans un CSV.
for category_name, category_url in get_categories(homepage_url).items():
    books = []

    for book_url in get_book_urls(category_url):
        books.append(extract_book_data(book_url))

    file_name = os.path.join("donnees", f"category_{clean_name(category_name)}_{date.today()}.csv")

    with open(file_name, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)

    print(f"{category_name}: {len(books)} books and images saved")
