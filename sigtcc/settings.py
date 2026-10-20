"""Configurações do projeto Django do SIGTCC.

Segredos e dados do ambiente vêm do arquivo .env (PGCS 3.4), lido pelo python-dotenv.
Decisões registradas em specs/001-modelo-dados/research.md (D1, D2, D4, R1).

[infraestrutura da feature 001, sem US específica]
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Raiz do repositório (onde ficam manage.py, .env e docs/).
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

# Sem django.contrib.admin: o modelo Usuarios não tem is_staff nem permissões (research D1).
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "sigtcc.apps.cadastro",
    "sigtcc.apps.defesa",
    "sigtcc.apps.relatorios",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sigtcc.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "sigtcc" / "templates"],
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

WSGI_APPLICATION = "sigtcc.wsgi.application"

# PostgreSQL 16 (constituição, princípio IV).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "sigtcc"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Usuarios do dicionário de dados como modelo de usuário (research D1).
AUTH_USER_MODEL = "cadastro.Usuarios"

# Definidos pela US-10 (RBN-CAD-06.3); fora do escopo desta feature.
AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "pt-br"
# Fuso único do NUCOMP; datas e horas sem fuso, como as colunas TIMESTAMP do dicionário (R1).
TIME_ZONE = "America/Manaus"
USE_I18N = True
USE_TZ = False

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "sigtcc" / "static"]

# Assinaturas e PDFs gerados; pasta fora do Git (PGCS 3.4).
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "sigtcc" / "media"

# Inteiro de 32 bits, igual ao INT do dicionário (research D4).
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Cache em arquivo para o bloqueio de login da US-11 (RBN-CAD-06.6), research D2.
_cache_dir = Path(os.getenv("CACHE_DIR", "cache"))
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(_cache_dir if _cache_dir.is_absolute() else BASE_DIR / _cache_dir),
    }
}
