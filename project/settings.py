"""
Django settings for the project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(PROJECT_DIR)

DATABASES = {}

try:
    from local_settings import LOCAL_DEBUG, LOCAL_DATABASES
except:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config()
    DEBUG = True
else:
    DATABASES.update(LOCAL_DATABASES)
    DEBUG = LOCAL_DEBUG

# email settings
# EMAIL_BACKEND = 'django_ses.SESBackend'#

email_settings = {
    'EMAIL_SENDER_NAME': "Sender name",
    'SENDER_EMAIL': 'sender email',

    # Amazon AWS settings
    'AWS_ACCESS_KEY_ID': 'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY': 'AWS_SECRET_ACCESS_KEY',
    'ENABLE_EMAILS': False,
}

try:
    from local_settings import LOCAL_EMAIL_SETTINGS
except:
    # heroku conf
    email_settings.update(os.environ)
else:
    email_settings.update(LOCAL_EMAIL_SETTINGS)

EMAIL_SENDER_NAME = email_settings['EMAIL_SENDER_NAME']
SENDER_EMAIL = email_settings['SENDER_EMAIL']

AWS_ACCESS_KEY_ID = email_settings['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = email_settings['AWS_SECRET_ACCESS_KEY']

ENABLE_EMAILS = email_settings['ENABLE_EMAILS']

# TEST should be true if we are running python tests
TEST = 'test' in sys.argv

if TEST:
    try:
        DATABASES['default'] = DATABASES['test']
        del DATABASES['test']
    except KeyError as e:
        print "%s is not defined in the DATABASES dict" % e.message
        print "Using default in-memory DB for tests"
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ":memory:",
                "HOST": "",
                "USER": "",
                "PASSWORD": "",
            }
        }

TEMPLATE_DEBUG = DEBUG

# Since we are using our custom user model, we need to set the authentication
# backend to the CustomBackend, so it returns the User model
AUTHENTICATION_BACKENDS = (
    'users.backends.CustomBackend',
)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Santiago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# SECURITY WARNING: keep the secret key used in production secret!
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'CHANGE ME'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('pyjade.ext.django.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'project.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/'),
)

INSTALLED_APPS = (
    'bootstrap_admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.gis',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    "compressor",
    'base',
    'users',
    'django.contrib.admin',
    'django_tables2',
)
# Set the apps that are installed locally
try:
    from local_settings import LOCALLY_INSTALLED_APPS
except:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + LOCALLY_INSTALLED_APPS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# set the precompilers for less and jade client templates
COMPRESS_PRECOMPILERS = (
    ('text/less', 'node_modules/less/bin/lessc {infile} > {outfile}'),
    ('text/jade', 'base.filters.jade.JadeCompilerFilter'),
)

# user loggin
LOGIN_REDIRECT_URL = "/"

# Tuple of IP addresses, as strings, that:
#   * See debug comments, when DEBUG is true
#   * Receive x-headers
INTERNAL_IPS = ('127.0.0.1',)

# Hosts/domain names that are valid for this site.
# "*" matches anything, ".example.com" matches example.com and all subdomains
ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'users.User'

RECAPTCHA_PUBLIC = '6LfLr90SAAAAABRD5AIfqIIYyIJ8Ls698OkQacNy'
RECAPTCHA_PRIVATE = '6LfLr90SAAAAAMJ63_e1jrxg-31NAJynZtF3VGmJ'
