import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

BASE_DIR=Path(__file__).resolve().parent.parent
DEBUG=os.getenv('DJANGO_DEBUG','false').lower()=='true'
DEMO_MODE=os.getenv('NEXUSDESK_DEMO_MODE','false').lower()=='true'
if DEMO_MODE and DEBUG:
    raise ImproperlyConfigured('Public demo must not run in debug mode')
SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY='dev-only-key-not-for-production-change-me'
    else:
        raise ImproperlyConfigured('Set DJANGO_SECRET_KEY in the environment')
ALLOWED_HOSTS=[x.strip() for x in os.getenv('DJANGO_ALLOWED_HOSTS','127.0.0.1,localhost').split(',') if x.strip()]
if os.getenv('RENDER_EXTERNAL_HOSTNAME'):
    ALLOWED_HOSTS.append(os.environ['RENDER_EXTERNAL_HOSTNAME'])
CSRF_TRUSTED_ORIGINS=[x.strip() for x in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS','').split(',') if x.strip()]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','desk']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','nexusdesk.demo_guard.DemoGuardMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='nexusdesk.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='nexusdesk.wsgi.application'
DATABASES={'default':dj_database_url.config(default='sqlite:///'+str(BASE_DIR/'db.sqlite3'),conn_max_age=60,conn_health_checks=True)}
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
    SECURE_HSTS_SECONDS=31536000 if os.getenv('DJANGO_ENABLE_HSTS','false').lower()=='true' else 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS=False
