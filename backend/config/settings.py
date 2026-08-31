"""
Django settings for MCWallet.

Configuration de l'environnement de développement de MCWallet.

Ce fichier contient les paramètres principaux de Django :
- sécurité
- applications installées
- middleware
- base de données PostgreSQL
- internationalisation
- fichiers statiques
- configuration des emails

Les informations sensibles sont chargées depuis le fichier .env
situé à la racine du projet MCWallet.
"""

from datetime import timedelta
from pathlib import Path
import os

from dotenv import load_dotenv


# ============================================================
# CHEMINS DU PROJET
# ============================================================

# BASE_DIR pointe vers :
#
# C:\Users\Poupou\Desktop\MCWallet\backend
#
# puisque settings.py se trouve dans :
#
# MCWallet/backend/config/settings.py

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# VARIABLES D'ENVIRONNEMENT
# ============================================================

# Notre fichier .env se trouve à la racine de MCWallet :
#
# MCWallet/
# ├── .env
# └── backend/
#
# BASE_DIR.parent permet donc de remonter de :
#
# MCWallet/backend
#
# vers :
#
# MCWallet

ENV_FILE = BASE_DIR.parent / ".env"

# Charge les variables présentes dans .env.
load_dotenv(ENV_FILE)


# ============================================================
# SÉCURITÉ DJANGO
# ============================================================

# La clé secrète n'est pas écrite directement dans le code.
# Elle est récupérée depuis le fichier .env.
#
# .env :
# DJANGO_SECRET_KEY=...

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")


# Mode développement.
#
# IMPORTANT :
# DEBUG=True est uniquement destiné au développement local.
# Nous modifierons cette configuration avant la mise en
# production de MCWallet.

DEBUG = True


# En développement local, Django accepte les requêtes provenant
# de localhost et de 127.0.0.1.

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]


# ============================================================
# APPLICATIONS DJANGO
# ============================================================

INSTALLED_APPS = [

    # --------------------------------------------------------
    # Applications natives de Django
    # --------------------------------------------------------

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # --------------------------------------------------------
    # Django REST Framework
    # --------------------------------------------------------

    "rest_framework",

    # --------------------------------------------------------
    # Applications MCWallet
    # --------------------------------------------------------

    # Application utilisateurs.
    #
    # Le chemin Python réel est apps.users.
    # Son label Django est "users", défini dans apps.py.
    "apps.users",
    "apps.wallets",
    "apps.transactions",

    # Futures applications métier.
    #
    # Elles seront ajoutées progressivement.
    #
    # "apps.wallets",
    # "apps.transactions",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URLS
# ============================================================

ROOT_URLCONF = "config.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Nous pourrons ajouter un dossier templates global
        # plus tard si nécessaire.
        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================================================
# SERVEUR WSGI
# ============================================================

WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# BASE DE DONNÉES
# ============================================================

# MCWallet utilise PostgreSQL.
#
# Les informations de connexion ne sont PAS écrites directement
# ici.
#
# Elles viennent du fichier .env :
#
# POSTGRES_DB
# POSTGRES_USER
# POSTGRES_PASSWORD
# POSTGRES_HOST
# POSTGRES_PORT
#
# Architecture :
#
# Django
#     ↓
# Django Database Backend
#     ↓
# psycopg
#     ↓
# PostgreSQL
#     ↓
# database "mcwallet"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}


# ============================================================
# VALIDATION DES MOTS DE PASSE
# ============================================================

# Ces validateurs sont fournis par Django.
#
# Ils permettent de contrôler les mots de passe lors de
# l'utilisation du système d'authentification Django.

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ============================================================
# INTERNATIONALISATION
# ============================================================

# Langue par défaut de MCWallet.

LANGUAGE_CODE = "fr-fr"


# Fuseau horaire utilisé par MCWallet.
#
# Cameroon = Africa/Douala

TIME_ZONE = "Africa/Douala"


# Active le système d'internationalisation.

USE_I18N = True


# Django stocke les dates/heures de manière timezone-aware.

USE_TZ = True


# ============================================================
# FICHIERS STATIQUES
# ============================================================

# URL utilisée pour accéder aux fichiers statiques :
#
# CSS
# JavaScript
# Images statiques

STATIC_URL = "static/"


# Dossier dans lequel Django pourra collecter les fichiers
# statiques pour un futur déploiement.

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# FICHIERS MÉDIA
# ============================================================

# Les fichiers envoyés par les utilisateurs seront stockés
# dans ce dossier en développement.
#
# Exemples futurs :
# - justificatifs de dépôt
# - documents
# - pièces jointes

MEDIA_URL = "media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# EMAIL
# ============================================================

# Pour le développement local, nous n'envoyons pas réellement
# les emails.
#
# Django affiche les emails directement dans le terminal.
#
# Cela nous permettra de développer et tester gratuitement
# le système d'inscription, récupération de compte, etc.

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ============================================================
# CONFIGURATION DJANGO REST FRAMEWORK
# ============================================================

# Configuration de base de Django REST Framework.
#
# Nous garderons cette section volontairement minimale pour
# l'instant.
#
# Lorsque nous commencerons l'API MCWallet, nous définirons
# précisément :
#
# - authentification
# - permissions
# - pagination
# - throttling
# - gestion des erreurs

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}


# ============================================================
# CONFIGURATION JWT
# ============================================================

SIMPLE_JWT = {
    # Durée pendant laquelle le token d'accès reste valide.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),

    # Durée pendant laquelle le refresh token peut être utilisé.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    # Le refresh token permet d'obtenir un nouvel access token.
    "ROTATE_REFRESH_TOKENS": True,

    # Après rotation, l'ancien refresh token est blacklisté.
    "BLACKLIST_AFTER_ROTATION": True,

    # Utilisation du format standard JWT.
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ============================================================
# CLÉ PRIMAIRE PAR DÉFAUT
# ============================================================

# Django utilisera BigAutoField pour les nouvelles tables
# lorsqu'aucun type de clé primaire n'est spécifié.

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# MODÈLE UTILISATEUR PERSONNALISÉ
# ============================================================

# MCWallet utilise son propre modèle User au lieu du User
# standard fourni par Django.
#
# Le label "users" correspond au label défini dans :
#
# apps/users/apps.py
#
# avec :
#
# name = "apps.users"
# label = "users"

AUTH_USER_MODEL = "users.User"

# ---------------------------------------------------------------------------
# BACKENDS D'AUTHENTIFICATION
# ---------------------------------------------------------------------------
#
# MCWallet permet la connexion avec :
# - une adresse email ;
# - OU un numéro de téléphone.
#
# Le backend personnalisé recherche l'utilisateur avec
# l'identifiant fourni puis vérifie son mot de passe.
#

AUTHENTICATION_BACKENDS = [
    "apps.users.backends.EmailOrPhoneBackend",
]