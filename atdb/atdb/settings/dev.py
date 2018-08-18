from atdb.settings.base import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["80.101.27.83","localhost","192.168.178.32","127.0.0.1"]
CORS_ORIGIN_ALLOW_ALL = True

#####################################################
# These settings mainly deal with https.
# See http://django-secure.readthedocs.io/en/latest/middleware.html
# Check the warning and instructions with:
# (.env) atdb@/var/.../atdb ./manage.py check --deploy --settings=atdb.settings.prod
#####################################################
# Assume SSL is correctly set up.
SSL_ENABLED = False
if SSL_ENABLED:
    # True: Django now checks that cookies are ONLY sent over SSL.
    # https://docs.djangoproject.com/en/1.11/ref/settings/#session-cookie-secure
    SESSION_COOKIE_SECURE = True
    # True: Django now checks that csrf tokens are ONLY sent over SSL.
    # https://docs.djangoproject.com/en/1.11/ref/settings/#csrf-cookie-secure
    CSRF_COOKIE_SECURE = True
    # True: Always redirect requests back to https (currently ignored as Nginx should enforces https).
    #       Alternatively, enable and add set SECURE_PROXY_SSL_HEADER.
    SECURE_SSL_REDIRECT = False
    # Setting this to a non-zero value, will default the client UA always to connect over https.
    # Unclear how or if this possibly affects other *.astron.nl domains. Especially, if these do
    # not support https whether this option then breaks those http-only locations.
    # SECURE_HSTS_SECONDS = 31536000

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
         'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'USER': 'atdb_admin',
         'PASSWORD': 'atdb123',

         # database runs locally in postgres
         'NAME': 'atdb_trunk',
         'HOST': 'localhost',
         'PORT': '',

         # database runs on a virtual machine
         # 'HOST': 'alta-sys-db.astron.nl',
         # 'PORT': '5432',
         # 'NAME': 'altadb'
    },
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

