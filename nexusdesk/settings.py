import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR=Path(__file__).resolve().parent.parent
DEBUG=os.getenv('DJANGO_DEBUG','false').lower()=='true'
SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY='dev-only-key-not-for-production-change-me'
    else:
        raise ImproperlyConfigured('Set DJANGO_SECRET_KEY in the environment')
ALLOWED_HOSTS=[x.strip() for x in os.getenv('DJANGO_ALLOWED_HOSTS','127.0.0.1,localhost').split(',') if x.strip()]
CSRF_TRUSTED_ORIGINS=[x.strip() for x in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS','').split(',') if x.strip()]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','desk']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='nexusdesk.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='nexusdesk.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'
TIME_ZONE='UTC'
USE_I18N=True
USE_TZ=True
STATIC_URL='static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STORAGES={'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='login'
LOGIN_REDIRECT_URL='dashboard'
LOGOUT_REDIRECT_URL='login'
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
CSRF_COOKIE_SAMESITE='Lax'
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_REFERRER_POLICY='strict-origin-when-cross-origin'
X_FRAME_OPTIONS='DENY'
if not DEBUG:
    SESSION_COOKIE_SECURE=True
    CSRF_COOKIE_SECURE=True
    SECURE_SSL_REDIRECT=os.getenv('DJANGO_SECURE_SSL_REDIRECT','true').lower()=='true'
    SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
