import os
from ctf_gameserver.web.base_settings import *  

DEBUG = False
SECRET_KEY = os.environ['CTF_WEB_SECRET_KEY']

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('CTF_ALLOWED_HOSTS', '').split(',') if h.strip()]

HTTPS = os.environ.get('CTF_HTTPS', '0') == '1'
if HTTPS:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('CTF_DBHOST', 'gs-postgres'),
        'PORT': os.environ.get('CTF_DBPORT', '5432'),
        'NAME': os.environ.get('CTF_DBNAME', 'ctf'),
        'USER': os.environ.get('CTF_DBUSER', 'ctf'),
        'PASSWORD': os.environ.get('CTF_DBPASSWORD', 'ctf'),
        'CONN_MAX_AGE': 60,
    }
}

CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

STATIC_ROOT = os.environ.get('CTF_STATIC_ROOT', '/data/static')
MEDIA_ROOT = os.environ.get('CTF_MEDIA_ROOT', '/data/uploads')
TEAM_DOWNLOADS_ROOT = os.environ.get('CTF_TEAM_DOWNLOADS_ROOT', '/data/team_downloads')

EMAIL_BACKEND = os.environ.get('CTF_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.environ.get('CTF_FROM_EMAIL', 'ctf@localhost')

TIME_ZONE = os.environ.get('CTF_TIMEZONE', 'UTC')
FIRST_DAY_OF_WEEK = 1