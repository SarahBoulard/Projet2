import csv
import os
import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def extraire_donnees_livre(url):
    reponse = requests.get(url)
    soup = BeautifulSoup(reponse.content, "html.parser")

    tableau = {ligne.th.text: ligne.td.text for ligne in soup.find_all("tr")}

    nombre_disponible = re.search(r"\d+", tableau["Availability"]).group()

    # Certains livres n'ont pas de description
    description = ""
    div_description = soup.find("div", id="product_description")
    if div_description:
        description = div_description.find_next_sibling("p").text

    categorie = soup.find("ul", class_="breadcrumb").find_all("a")[2].text

    notes = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    note_en_lettres = soup.find("p", class_="star-rating")["class"][1]

    source_image = soup.find("div", id="product_gallery").find("img")["src"]

    # Les clés restent en anglais : ce sont les en-têtes imposés par les exigences
    return {
        "product_page_url": url,
        "universal_product_code (upc)": tableau["UPC"],
        "title": soup.find("h1").text,
        "price_including_tax": tableau["Price (incl. tax)"],
        "price_excluding_tax": tableau["Price (excl. tax)"],
        "number_available": nombre_disponible,
        "product_description": description,
        "category": categorie,
        "review_rating": notes[note_en_lettres],
        "image_url": urljoin(url, source_image),
    }


def recuperer_urls_livres(url_categorie):
    urls_livres = []
    url_page = url_categorie

    # Tant qu'il y a une page à visiter
    while url_page:
        reponse = requests.get(url_page)
        soup = BeautifulSoup(reponse.content, "html.parser")

        for lien in soup.select("article.product_pod h3 a"):
            urls_livres.append(urljoin(url_page, lien["href"]))

        # Lien "next" : s'il existe, on passe à la page suivante, sinon on s'arrête
        lien_suivant = soup.find("li", class_="next")
        if lien_suivant:
            url_page = urljoin(url_page, lien_suivant.find("a")["href"])
        else:
            url_page = None

    return urls_livres


def recuperer_categories(url_accueil):
    reponse = requests.get(url_accueil)
    soup = BeautifulSoup(reponse.content, "html.parser")

    # Menu de gauche : on prend les sous-catégories, pas le lien général "Books"
    categories = {}
    for lien in soup.select("div.side_categories ul li ul li a"):
        categories[lien.text.strip()] = urljoin(url_accueil, lien["href"])

    return categories


url_accueil = "https://books.toscrape.com/index.html"

# Tous les CSV sont rangés dans un même dossier
os.makedirs("donnees", exist_ok=True)

for nom_categorie, url_categorie in recuperer_categories(url_accueil).items():
    livres = []
    for url_livre in recuperer_urls_livres(url_categorie):
        livres.append(extraire_donnees_livre(url_livre))

    # Nom du fichier : donnees/categorie_mystery_2026-10-06.csv
    nom_nettoye = re.sub(r"[^a-zA-Z0-9]+", "_", nom_categorie).strip("_").lower()
    nom_fichier = os.path.join("donnees", f"categorie_{nom_nettoye}_{date.today()}.csv")

    with open(nom_fichier, "w", newline="", encoding="utf-8") as fichier_csv:
        ecrivain = csv.DictWriter(fichier_csv, fieldnames=livres[0].keys())
        ecrivain.writeheader()
        ecrivain.writerows(livres)

    print(f"{nom_categorie} : {len(livres)} livres enregistrés dans {nom_fichier}")
