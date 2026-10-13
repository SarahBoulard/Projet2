# Books to Scrape : suivi des prix

Version bêta d'un scraper pour Books Online. Le script parcourt le site [Books to Scrape](https://books.toscrape.com/), récupère les informations de tous les livres de toutes les catégories et télécharge leurs couvertures.

Les prix sont relevés au moment où le script est lancé. Il n'y a pas de suivi automatique dans le temps.

## Prérequis

- Python 3.10 ou plus récent
- Git

## Installation

1. Cloner le repository et entrer dans le dossier :

   ```bash
   git clone <url-du-repository>
   cd <nom-du-dossier>
   ```

2. Créer l'environnement virtuel :

   ```bash
   python -m venv env
   ```

3. Activer l'environnement virtuel :

   - Windows (PowerShell) :

     ```bash
     env\Scripts\Activate.ps1
     ```

   - Windows (invite de commandes) :

     ```bash
     env\Scripts\activate
     ```

   - macOS / Linux :

     ```bash
     source env/bin/activate
     ```

4. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

## Lancer le script

```bash
python scraper.py
```

Le script affiche une ligne par catégorie traitée. Il visite environ 1 000 pages et télécharge 1 000 images, comptez quelques minutes selon la connexion.

## Données produites

Tout est enregistré dans un dossier `donnees/`, créé automatiquement :

```
donnees/
├── categorie_mystery_2026-10-13.csv
├── categorie_travel_2026-10-13.csv
├── ...
└── images/
    ├── mystery/
    │   ├── e10e1e165dc8be4a.jpg
    │   └── ...
    └── travel/
        └── ...
```

- Un fichier CSV par catégorie, nommé avec la catégorie et la date d'exécution.
- Une image par livre, rangée dans le dossier de sa catégorie et nommée avec l'UPC du livre. Pour retrouver l'image d'un livre, il suffit de prendre son UPC dans le CSV.

Chaque CSV contient les colonnes suivantes :

| Colonne | Contenu |
|---|---|
| `product_page_url` | URL de la page du livre |
| `universal_product_code (upc)` | Code UPC |
| `title` | Titre |
| `price_including_tax` | Prix TTC |
| `price_excluding_tax` | Prix HT |
| `number_available` | Nombre d'exemplaires en stock |
| `product_description` | Description (vide si le livre n'en a pas) |
| `category` | Catégorie |
| `review_rating` | Note de 1 à 5 |
| `image_url` | URL de la couverture |

Le dossier `donnees/` n'est pas versionné (voir `.gitignore`).
