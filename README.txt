====================================================
  CIV LOCATION — Plateforme de location de véhicules
====================================================

PRÉREQUIS
---------
- Python 3.10 ou supérieur
- pip

INSTALLATION
------------

1. Cloner / décompresser le projet dans un dossier

2. Créer un environnement virtuel :
   python -m venv venv

3. Activer l'environnement virtuel :
   - Windows : venv\Scripts\activate
   - Linux/Mac : source venv/bin/activate

4. Installer les dépendances :
   pip install -r requirements.txt

5. Copier le fichier d'environnement :
   cp .env.example .env
   (Modifier la SECRET_KEY dans .env)

6. Appliquer les migrations :
   python manage.py migrate

7. Créer le compte administrateur par défaut :
   python manage.py init_admin

8. Lancer le serveur :
   python manage.py runserver

9. Ouvrir dans le navigateur :
   http://127.0.0.1:8000/

ACCÈS
-----
- Site public       : http://127.0.0.1:8000/
- Espace interne    : http://127.0.0.1:8000/gestion/connexion/
- Espace partenaire : http://127.0.0.1:8000/partenaire/connexion/

COMPTE ADMINISTRATEUR PAR DÉFAUT
---------------------------------
  Email    : franckyaboudou@gmail.com
  Mot de passe : AdminDefaut

STRUCTURE DES DOSSIERS
-----------------------
  civ_location/   → Configuration principale Django
  public/         → Application site public (clients)
  gestion/        → Application espace interne (admin + gestionnaires)
  partenaire/     → Application espace partenaires
  media/          → Fichiers uploadés (photos, documents)

NOTES
-----
- La base de données SQLite est créée automatiquement (db.sqlite3)
- Les fichiers médias sont stockés dans le dossier media/
- Pour la mise en production, configurer DEBUG=False et ALLOWED_HOSTS dans .env

====================================================
  CONFIGURATION EMAIL (NOTIFICATIONS)
====================================================

Pour recevoir les notifications par email, suivez ces étapes :

ÉTAPE 1 — Activer la validation en 2 étapes Google
  → https://myaccount.google.com/security

ÉTAPE 2 — Générer un mot de passe d'application
  → https://myaccount.google.com/apppasswords
  → Choisir "Mail" + "Ordinateur Windows"
  → Copier le mot de passe généré (16 caractères)

ÉTAPE 3 — Configurer le fichier .env
  Ouvrez le fichier .env et ajoutez :

  EMAIL_HOST_USER=franckyaboudou@gmail.com
  EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx

  (remplacez par votre vrai mot de passe d'application)

NOTIFICATIONS ENVOYÉES AUTOMATIQUEMENT
  - Nouvelle réservation client → franckyaboudou@gmail.com
  - Nouvelle demande partenaire → franckyaboudou@gmail.com

NOTE : Sans configuration email, le site fonctionne 
normalement. Les emails sont envoyés en mode silencieux 
(fail_silently=True), donc aucune erreur n'est levée.
