# Copro API Project

Une API Django REST pour la calculer des statistiques au sujet des charges de copropriétés.

## Installation et configuration

### 1. Cloner le repository

```bash
git clone https://github.com/NicoZeiss/copro_backend.git
cd copro
```

### 2. Créer un environnement virtuel

```bash
# Créer l'environnement virtuel
python -m venv venv

# L'activer (Linux/Mac)
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données

Le projet utilise SQLite par défaut. Pour initialiser la base de données :

```bash
# Appliquer les migrations
python manage.py migrate

# (Optionnel) Créer un superutilisateur
python manage.py createsuperuser
```

## Lancement du projet

### Démarrer le serveur de développement

```bash
python manage.py runserver
```

Le serveur sera accessible à l'adresse : http://127.0.0.1:8000/

### Accès à l'administration Django

L'interface d'administration est disponible à : http://127.0.0.1:8000/admin/

### Documentation API

La documentation automatique de l'API est disponible grâce à `drf-spectacular` :
- Interface Swagger UI : http://127.0.0.1:8000/api/schema/swagger-ui/

## Structure du projet

```
copro/
├── config/          # Configuration Django
├── copro/           # Application principale
├── db.sqlite3       # Base de données SQLite
├── manage.py        # Script de gestion Django
└── requirements.txt # Dépendances Python
```

## Technologies utilisées

- **Django 5.2.4** - Framework web Python
- **Django REST Framework 3.16.0** - API REST
- **drf-spectacular 0.28.0** - Documentation automatique de l'API
- **Pandas 2.3.1** - Manipulation et analyse de données
- **Numpy 2.3.1** - Calculs numériques et opérations sur les tableaux
- **requests 2.32.4** - Bibliothèque HTTP pour les requêtes externes
- **SQLite** - Base de données (développement)

## Remplir la base de données à partir d'un CSV
- Placer le/les fichier(s) CSV dans ***copro/resources/***

```bash
# Importer le CSV dans la BDD
# (Optionnel, 50_000 par défaut) --chunksize <int:TAILLE_DES_CHUNKS>
python manage.py import_csv <NOM_DU_FICHIER>.csv
```
