from .base import *

DEBUG=False

ADMIN = (
    ('Ashok Panigrahi', 'ashokoffice@yahoo.co.uk')
)

ALLOWED_HOSTS = ['*']

default_database = environ.get('DJANGO_DEFAULT_DATABASE','main')
DATABASES['default'] = DATABASES[default_database]