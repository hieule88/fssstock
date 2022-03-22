"""
Django settings for abnormalstock project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os # needed by code below
import os.path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+zqjb62@*cz&x_f=-y1$djcew(kt)21wdy9)+yebauixu&eu4i'

# SOCIAL_AUTH_AUTH0_SCOPE = [
#     'openid',
#     'profile',
#     'email'
# ]
# AUTHENTICATION_BACKENDS = {
#     "auth0login.auth0backend.Auth0",
#     "django.contrib.auth.backends.ModelBackend",
# }
LOGIN_URL = "/login/auth0"
LOGIN_REDIRECT_URL = "/"


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

ALLOWED_HOSTS = ['*']

# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = [
    'abnormaldetect',
    'sitetree',
    'crispy_forms',
    #'background_task',
    'django.contrib.admin',
    'django.contrib.auth',  #Core authentication framework and its default models.
    'django.contrib.contenttypes',  #Django content type system (allows permissions to be associated with models).
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

#SESSION_COOKIE_SECURE = False
#SESSION_EXPIRE_AT_BROWSER_CLOSE = False
#CSRF_COOKIE_SECURE = False
#CSRF_COOKIE_DOMAIN = None
#CSRF_USE_SESSIONS = False

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', #Manages sessions across requests
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  #Associates users with requests using sessions.
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'abnormalstock.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'abnormalstock.wsgi.application'
CRISPY_TEMPLATE_PACK = 'bootstrap4'
CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'rpc://localhost'
BYPASS_AUTHENTICATE = True


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

BACKEND_DB = 'RISK_USER/RISK_USER@192.168.1.30:1521/orcl.fss.com.vn'
BACKEND_IP_HOST_DB = '192.168.1.30'
BACKEND_PORT_DB='1521'
BACKEND_SERVICE_NAME_USE = 'ORCL.FSS.COM.VN'
BACKEND_USER_DB='RISK_USER'
BACKEND_PASS_DB = 'RISK_USER'
USE_THOUSAND_SEPARATOR = True

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media/')
TEMPLATE_DIRS = [
    os.path.join(PROJECT_PATH, 'templates/').replace('\\','/'),
    "C:/work/FSS_stock/abnormalstock/abnormaldetect/templates".replace('\\','/'),
]

# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
# #     'django.template.loaders.eggs.Loader',
# )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


# #STATIC_URL = '/static/'
# STATIC_ROOT = 'C:/work/FSS_stock/abnormalstock/abnormaldetect/static'
# STATICFILES_DIRS = ( os.path.join('static'), )
# MEDIA_URL = 'C:/work/FSS_stock/abnormalstock/abnormaldetect/media/'
# MEDIA_ROOT = os.path.join(REPOSITORY_ROOT, 'media/')

REPOSITORY_ROOT = os.path.dirname(BASE_DIR)

STATIC_URL = '/static/'
STATIC_ROOT = "C:\work\FSS_stock\abnormalstock\abnormaldetect\static".replace('\\','/')
# STATICFILES_DIRS = ["C:\work\FSS_stock\abnormalstock\abnormaldetect\static".replace('\\','/'),]

# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(REPOSITORY_ROOT, 'abnormaldetect/media/')

# iterable
YESNO_CHOICES =(
    ("Y", "Yes"),
    ("N", "No"),
)

TAGCOLOR_CHOICES =(
    ("A", "All"),
    ("G", "Good"),
    ("P", "Primary"),
    ("S", "Secondary"),
)

YEAR_CHOICES =(
    ("2020", "Up to 2020"),
    ("2019", "Up to 2019"),
    ("2018", "Up to 2018"),
)

AGE_CHOICES =(
    ("0", "No limit"),
    ("2", "Atleast 2 years"),
    ("5", "Atleast 5 years"),
)

CAPITAL_CHOICES =(
    ("0", "No limit"),
    ("5", "Atleast 5 bilions VND"),
    ("20", "Atleast 20 bilions VND"),
)

TTR_CHOICES =(
    ("A", "A: TTR(Yes), Fraud(No)"),
    ("B", "B: TTR(Yes), TTR(No), Fraud(No)"),
    ("C", "C: TTR(Yes), Fraud(Yes), Fraud(No)"),
    ("D", "D: Fraud(Yes), Fraud(No)"),
)

COMMAND_CHOICES =(
    ("R", "Read"),
    ("W", "Write"),
    ("D", "Direct Write"),
)


QUERY_CHOICES =(
    ("D", "Data in detail"),
    ("P", "Prediction"),
    ("A", "Model Accurancy"),
#    ("L", "Logistic regression"),
#    ("S", "Scorecard"),
    ("I", "Checking CTBAOCAO"),
    ("K", "Checking CTPHANTICH"),
    ("R", "Reconcile"),
    ("X", "Task activies"),
    ("Z", "Summary all data"),
)

RISKPROFILE_CHOICES =(
    ("D", "DTNT"),
    ("N", "NGANH"),
    ("T", "TINH"),
)

PREDICTION_CHOICES =(
    ("A", "All model"),
    ("V", "VAR"),
)

ETL_CHOICES =(
    ("I", "CTBAOCAO"),
    ("K", "CTPHANTICH"),
)

ESTIMATE_CHOICES =(
    ("K_T_Z16", "K_T_Z16"),
    ("K_T_B06", "K_T_B06"),    
    ("K_C_V22", "K_C_V22"),
    ("K_C_V34", "K_C_V34"),
)

KRISET_CHOICES =(
    ("B", "Basic"),
    ("A", "Advanced"),
    ("C", "Cressey"),
    ("F", "Full (Advanced & Cressey)"),
    ("FS", "F-Score"),
    ("MS", "M-Score"),
    ("ZS", "Z-Score"),
    ("P", "Fundamental"),
)

EXPORT_CHOICES =(
    ("basic", "Export Basic"),
    ("all", "Export All"),
    ("selected", "Export Selected"),
)

INQUIRY_CHOICES =(
    ("A", "Model Accurancy"),
    ("D", "Data in detail"),
)