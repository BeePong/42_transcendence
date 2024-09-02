# settings.py

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure--5o3-*y!2w25g-%9h^8yt!z(!7f^p_xf8+x5u(9z#*^o#pxtq9",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "backendummy", "nginx", "c1r3p3.hive.fi"]

# Application definition

INSTALLED_APPS = [
    # My apps
    "beePong",
    "accounts",
    "tournament",
    # Third-party appsx
    "django_bootstrap5",
    # 'channels',
    "daphne",
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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

ROOT_URLCONF = "bpong_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bpong_project.wsgi.application"

ASGI_APPLICATION = "bpong_project.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
            # "capacity": 10,
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": "5432",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# My settings
# Tells Django which URL to redirect to after a successful login attempt.
LOGIN_REDIRECT_URL = "beePong:index"
# Tells Django to redirect logged-out users back to the home page
LOGOUT_REDIRECT_URL = "beePong:index"
LOGIN_URL = "accounts:login"

# List of trusted origins for CSRF protection
# Requests from these origins will be allowed to bypass the CSRF protection
CSRF_TRUSTED_ORIGINS = [
    "https://localhost",
    "https://127.0.0.1",
    "https://nginx",
    "https://localhost:8443",
    "https://c1r3p3.hive.fi:8443",
]

# Game settings TODO: use them in front-end and back-end
FIELD_WIDTH = 800
FIELD_HEIGHT = 500
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 26
PADDLE_SPEED = 20
BALL_RADIUS = 15
BALL_STARTING_SPEED = 5
BALL_SPEED_INCREMENT = 0
FPS = 15
MAX_SCORE = 50000
PADDING_THICKNESS = 7
THICK_BORDER_THICKNESS = 5
UPPER_LIMIT = PADDING_THICKNESS + PADDLE_HEIGHT / 2
LOWER_LIMIT = FIELD_HEIGHT - PADDING_THICKNESS - PADDLE_HEIGHT / 2

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": "WARNING",  # Change to DEBUG to increase verbosity
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console"],
#             "level": "WARNING",
#             "propagate": False,
#         },
#         "channels": {
#             "handlers": ["console"],
#             "level": "WARNING",
#             "propagate": True,
#         },
#     },
# }
