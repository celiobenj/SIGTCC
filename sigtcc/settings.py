"""Configurações do projeto Django do SIGTCC.

Segredos e dados do ambiente vêm do arquivo .env (PGCS 3.4), lido pelo python-dotenv.
Decisões registradas em specs/001-modelo-dados/research.md (D1, D2, D4, R1) e em
specs/003-acesso-login/research.md (A1, A2, A5, A6, A13, A19).

[infraestrutura da feature 001, sem US específica][infraestrutura da feature 003]
[US-11][RBN-CAD-06.4][RBN-CAD-06.6][FR-011][FR-029]
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# Raiz do repositório (onde ficam manage.py, .env e docs/).
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

# Ambiente de validação no Render (docs/deploy-render.md): o Render informa o endereço público
# em RENDER_EXTERNAL_HOSTNAME; ele entra nos hosts aceitos e nas origens confiáveis do CSRF.
RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")

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
    # Arquivos estáticos servidos pelo próprio Django com DEBUG = False (deploy).
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
                # Menu lateral por perfil e contador do sino (research A8). [FR-022][FR-025]
                "sigtcc.apps.cadastro.contexto.menu",
                "sigtcc.apps.cadastro.contexto.notificacoes_nao_lidas",
            ],
        },
    },
]

WSGI_APPLICATION = "sigtcc.wsgi.application"

# PostgreSQL 16 (constituição, princípio IV). No deploy, o banco vem de DATABASE_URL; sem ela,
# valem as variáveis DB_* do ambiente local.
if os.getenv("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.config()}
else:
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

# Login próprio: o backend só carrega o usuário da sessão; a senha é conferida em
# services.autenticar (research A1). [US-11][RBN-CAD-06.4]
AUTHENTICATION_BACKENDS = ["sigtcc.apps.cadastro.backends.SigtccBackend"]
LOGIN_URL = "cadastro:entrar"
LOGIN_REDIRECT_URL = "cadastro:painel"

# Regra de senha da US-10 e da US-12: 8 a 64 caracteres, 1 letra e 1 número (research A10).
# [US-10][RBN-CAD-06.3][US-12][RBN-CAD-06.5]
AUTH_PASSWORD_VALIDATORS = [{"NAME": "sigtcc.apps.cadastro.validators.RegraSenhaSigtcc"}]

# Sessão: termina após 60 minutos sem uso e ao fechar o navegador (spec Q18; research A6).
# [US-11][FR-011]
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
# Em produção (HTTPS), COOKIES_SEGUROS=True no .env (índice Q-27).
COOKIES_SEGUROS = os.getenv("COOKIES_SEGUROS", "False") == "True"
SESSION_COOKIE_SECURE = COOKIES_SEGUROS
CSRF_COOKIE_SECURE = COOKIES_SEGUROS
if COOKIES_SEGUROS:
    # Atrás do proxy HTTPS do Render: a conexão é segura quando o proxy diz que é.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Não afrouxar (A3, A11): o token dos links não vaza pelo Referer, e o navegador não adivinha
# o tipo dos arquivos enviados.
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True

# E-mail (research A5). [US-10][US-12][US-37][US-38]
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "10"))
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "nao-responda@uea.edu.br")
# Endereço base dos links enviados por e-mail.
SITE_URL_PADRAO = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
SITE_URL = os.getenv("SITE_URL", SITE_URL_PADRAO).rstrip("/")
# True só nos testes: o e-mail de "Esqueci minha senha" sai na própria requisição (A5).
SIGTCC_EMAIL_SINCRONO = False

LANGUAGE_CODE = "pt-br"
# Fuso único do NUCOMP; datas e horas sem fuso, como as colunas TIMESTAMP do dicionário (R1).
TIME_ZONE = "America/Manaus"
USE_I18N = True
USE_TZ = False

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "sigtcc" / "static"]
# Destino do collectstatic no deploy; fica fora do Git.
STATIC_ROOT = BASE_DIR / "staticfiles"

# Assinaturas e PDFs gerados; pasta fora do Git (PGCS 3.4).
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "sigtcc" / "media"

# Inteiro de 32 bits, igual ao INT do dicionário (research D4).
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


def _pasta(variavel, padrao):
    """Pasta do .env, relativa à raiz do repositório quando não for absoluta."""
    caminho = Path(os.getenv(variavel, padrao))
    return caminho if caminho.is_absolute() else BASE_DIR / caminho


# Cache padrão em arquivo (spec 001, research D2). O bloqueio de login da US-11 fica no alias
# próprio "acesso", que não é limpo junto com o padrão (research A2). [US-11][RBN-CAD-06.6]
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(_pasta("CACHE_DIR", "cache")),
    },
    "acesso": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(_pasta("CACHE_ACESSO_DIR", "cache_acesso")),
        "OPTIONS": {"MAX_ENTRIES": 100000},
    },
}

# Log de eventos de acesso, em arquivo, sem tabela (FR-029; spec Q21; research A13).
# [US-11][RBN-CAD-06.6][US-12][US-38][FR-029]
LOG_DIR = _pasta("LOG_DIR", "logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"acesso": {"format": "%(asctime)s | %(message)s"}},
    "handlers": {
        "arquivo_acesso": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "acesso.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "delay": True,
            "encoding": "utf-8",
            "formatter": "acesso",
        }
    },
    "loggers": {
        "sigtcc.acesso": {"handlers": ["arquivo_acesso"], "level": "INFO", "propagate": False}
    },
}
