from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

ADMINS = (('Alejandro', 'alejoveintimilla@gmail.com'),)  # Se utiliza para enviar emails de contacto
SERVER_EMAIL = "letraserrores@no-reply.com"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['LIBROS_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
HEROKU = True
HEROKU_DB = True
AMAZON_S3 = True

ALLOWED_HOSTS = ["*"]

CITIES_LIGHT_TRANSLATION_LANGUAGES = ['es']
CITIES_LIGHT_INCLUDE_COUNTRIES = ['EC']

# Context Processors
TEMPLATE_CONTEXT_PROCESSORS += (
    # 'perfiles.context_processors.procesar_ciudad',
    # 'perfiles.context_processors.procesar_perfil',
    # 'perfiles.context_processors.notificaciones'
    'perfiles.context_processors.admins_bcompartidas',  # unico context procesor mientras no haya perfiles abiertos
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect')

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'grupos',
    'libros',
    'perfiles',
    'comentarios',
    'notificaciones',
    'storages',
    'cities_light'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'letrasclub.urls'

WSGI_APPLICATION = 'letrasclub.wsgi.application'

# python social auth
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend'
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'letrasclub.utils.crear_perfil'
)

DATABASES = {}

if HEROKU_DB:
    DATABASES['default'] = dj_database_url.config()

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'letraslocaldb',
            'USER': 'alejandro',
            'PASSWORD': os.environ["POSTGRE_PSWD"]
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

TEMPLATE_DIRS = (BASE_DIR + "/templates/",)
FIXTURE_DIRS = (BASE_DIR + "/fixtures/",)

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_URL = '/static/'
STATIC_ROOT = '/'

if AMAZON_S3:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    AWS_ACCESS_KEY_ID = os.environ['AWSAccessKeyId']
    AWS_SECRET_ACCESS_KEY = os.environ['AWSSecretKey']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
    STATIC_URL = S3_URL
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Heroku
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Login settings
LOGIN_URL = "/libros/main/"
LOGIN_REDIRECT_URL = "/perfil/redirigir_login/"

if HEROKU:
    SOCIAL_AUTH_FACEBOOK_KEY = os.environ["SOCIAL_AUTH_FACEBOOK_KEY"]
    SOCIAL_AUTH_FACEBOOK_SECRET = os.environ["SOCIAL_AUTH_FACEBOOK_SECRET"]

    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ["SOCIAL_AUTH_GOOGLE_SECRET"]
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ["SOCIAL_AUTH_GOOGLE_KEY"]

    # Sendgrid
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
