"""
PRODUCTION Django settings for the CTF gameserver web component.

Unlike sim_settings.py, this is meant for a real competition:
  - DEBUG is off
  - SECRET_KEY, allowed hosts and paths come from the environment (see .env)
  - static files and uploads are served by nginx, not Django

Nothing secret lives in this file; all sensitive values are read from the
environment. Set them in the server's .env (which is gitignored). Generate the
secrets with ./scripts/gen-secrets.sh.
"""
import os

# pylint: disable=wildcard-import, unused-wildcard-import
from ctf_gameserver.web.base_settings import *  # noqa: F401,F403


# --- Core security ----------------------------------------------------------
DEBUG = False

# A long random string; fail loudly if it was not set.
SECRET_KEY = os.environ['CTF_WEB_SECRET_KEY']

# Hostnames / IPs the scoreboard is served under, comma-separated.
# e.g. CTF_ALLOWED_HOSTS="10.0.0.10,scoreboard.ctf.local"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('CTF_ALLOWED_HOSTS', '').split(',') if h.strip()]

# Set CTF_HTTPS=1 if TLS is terminated in front of nginx; makes cookies secure-only.
HTTPS = os.environ.get('CTF_HTTPS', '0') == '1'
if HTTPS:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

# --- Database ---------------------------------------------------------------
# The DB lives on the internal infra network and is firewalled off from teams,
# so its password is an internal credential rather than a competition secret.
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

# --- Caching / sessions -----------------------------------------------------
# Local-memory cache is plenty for a small event. For a larger one, switch to
# memcached (see the ctf-gameserver installation docs).
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# --- Files (served by nginx; see nginx.conf) --------------------------------
STATIC_ROOT = os.environ.get('CTF_STATIC_ROOT', '/data/static')
MEDIA_ROOT = os.environ.get('CTF_MEDIA_ROOT', '/data/uploads')
TEAM_DOWNLOADS_ROOT = os.environ.get('CTF_TEAM_DOWNLOADS_ROOT', '/data/team_downloads')

# --- Email ------------------------------------------------------------------
# Console backend just logs mails; point at a real SMTP server to actually send.
EMAIL_BACKEND = os.environ.get('CTF_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.environ.get('CTF_FROM_EMAIL', 'ctf@localhost')

# --- Misc -------------------------------------------------------------------
TIME_ZONE = os.environ.get('CTF_TIMEZONE', 'UTC')
FIRST_DAY_OF_WEEK = 1
