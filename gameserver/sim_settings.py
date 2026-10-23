"""
Django settings for the LOCAL SIM gameserver: dev server, permissive, auto-seed.
Do NOT use these for a real competition -- that is what prod_settings.py is for.
"""
import os

from ctf_gameserver.web.base_settings import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = os.environ.get('CTF_WEB_SECRET_KEY', 'sim-only-not-secret')  # nosec

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
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'range@localhost'

MEDIA_ROOT = '/data/uploads'
TEAM_DOWNLOADS_ROOT = '/data/team_downloads'

TIME_ZONE = 'UTC'
FIRST_DAY_OF_WEEK = 1

CSP_POLICIES = {
    'base-uri': ["'self'"],
    'connect-src': ["'self'"],
    'form-action': ["'self'"],
    'object-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'", "'unsafe-inline'"],
}
