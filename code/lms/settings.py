"""
Django settings untuk Django LMS Final Project

Stack:
- PostgreSQL    : database utama
- Redis         : cache, session, celery result backend
- MongoDB       : analytics & activity logging
- RabbitMQ      : message broker untuk Celery
- Celery        : async task processing
- Celery Beat   : periodic/scheduled tasks
"""

import os
from pathlib import Path
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# SECRET KEY — ambil dari env, fallback hanya untuk development lokal
# Di production WAJIB set env variable SECRET_KEY
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-only-change-in-production-final-project-2025'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')


# =============================================================================
# Aplikasi
# =============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "silk",             # query profiling
    "ninja_simple_jwt", # JWT authentication
    "courses",          # app utama LMS
    "analytics",        # analytics berbasis MongoDB
]


# =============================================================================
# Middleware
# =============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "silk.middleware.SilkyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lms.urls"

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

WSGI_APPLICATION = "lms.wsgi.application"


# =============================================================================
# Database — PostgreSQL, semua config dari env variable
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get('DB_NAME', 'lms_db'),
        "USER": os.environ.get('DB_USER', 'postgres'),
        "PASSWORD": os.environ.get('DB_PASSWORD', 'postgres'),
        "HOST": os.environ.get('DB_HOST', 'database'),
        "PORT": os.environ.get('DB_PORT', '5432'),
    }
}


# =============================================================================
# Password Validation
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True


# =============================================================================
# Static & Media
# =============================================================================

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# Django Silk — Query Profiling
# Dashboard: http://localhost:8000/silk/
# =============================================================================

SILKY_PYTHON_PROFILER = True
SILKY_META = True


# =============================================================================
# Redis Cache
# DB 0 : leaderboard (ZSet)
# DB 1 : cache & session
# DB 2 : Celery result backend
# =============================================================================

REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "lms",
        "TIMEOUT": 300,  # 5 menit default TTL
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = False


# =============================================================================
# MongoDB — Analytics & Activity Logging
# =============================================================================

MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017')
MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'lms_analytics')


# =============================================================================
# Celery — Async Task Queue (RabbitMQ broker + Redis result)
# =============================================================================

CELERY_BROKER_URL = os.environ.get(
    'CELERY_BROKER_URL',
    'amqp://admin:password123@rabbitmq:5672//'
)

CELERY_RESULT_BACKEND = os.environ.get(
    'CELERY_RESULT_BACKEND',
    f'{REDIS_URL}/2'
)

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Jakarta'
CELERY_RESULT_EXPIRES = 86400  # hasil task disimpan 1 hari

# Task retry config
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # retry setelah 60 detik


# =============================================================================
# Celery Beat — Jadwal Task Otomatis
# =============================================================================

CELERY_BEAT_SCHEDULE = {
    # Statistik harian — setiap tengah malam
    'daily-course-stats': {
        'task': 'courses.tasks.generate_daily_stats',
        'schedule': crontab(hour=0, minute=0),
    },
    # Cleanup log MongoDB lama — setiap jam 02:00
    'cleanup-old-activity-logs': {
        'task': 'courses.tasks.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0),
    },
}
