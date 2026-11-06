import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_CONFIG = BASE_DIR / ".local" / "database.json"
DATABASE_CONFIG = json.loads(LOCAL_CONFIG.read_text(encoding="utf-8")) if LOCAL_CONFIG.exists() else {}


def db_setting(name, default):
    return os.environ.get(name, DATABASE_CONFIG.get(name, default))


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "objectra-local-development-only")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "[::1]"]
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.staticfiles", "detector"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
}]
if DEBUG:
    TEMPLATES[0]["APP_DIRS"] = False
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]
WSGI_APPLICATION = "config.wsgi.application"
if os.getenv("LOCAL_SQLITE") == "1":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "local.sqlite3"}}
else:
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_setting("DB_NAME", "objectra"),
        "USER": db_setting("DB_USER", "objectra"),
        "PASSWORD": db_setting("DB_PASSWORD", ""),
        "HOST": db_setting("DB_HOST", "127.0.0.1"),
        "PORT": db_setting("DB_PORT", "5432"),
        "OPTIONS": {"connect_timeout": 5},
    }}
LANGUAGE_CODE = "es-ec"
TIME_ZONE = "America/Guayaquil"
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_MEMORY_SIZE = 3 * 1024 * 1024
SYSTEM_NAME = os.getenv("SYSTEM_NAME", "OBJECTRA")

MODEL_PATH = Path(os.getenv(
    "YOLO_MODEL_PATH",
    str(BASE_DIR / "models" / "yolo11s-seg-eva-320_openvino_model"),
))
QUALITY_MODELS = {
    "fast": (320, MODEL_PATH),
    "balanced": (480, BASE_DIR / "models" / "yolo11s-seg-eva-480_openvino_model"),
    "detail": (640, BASE_DIR / "models" / "yolo11s-seg_openvino_model"),
}
