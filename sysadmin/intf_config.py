import os
from os import environ
from django.conf import settings
from django.db import connection, connections

default_database = environ.get('DJANGO_INTF_DATABASE','current')
DJANGO_DB_NAME = environ.get('DJANGO_DB_NAME','oratech')
DJANGO_DB_USER = environ.get('DJANGO_DB_USER',"")
DJANGO_DB_PWD = environ.get('DJANGO_DB_PWD',"")
DJANGO_DB_HOST = environ.get('DJANGO_DB_HOST',"")
DJANGO_DB_PORT = environ.get('DJANGO_DB_PORT',"1521")

INTF_DATABASES = {
    'current': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': DJANGO_DB_NAME,
        'USER': DJANGO_DB_USER,
        'PASSWORD': DJANGO_DB_PWD,
        'HOST': DJANGO_DB_HOST,
        'PORT': DJANGO_DB_PORT,
    },
}

def set_connection(p_user:str = "",
                    p_pwd:str = "",
                    p_host:str = 'localhost',
                    p_port:str='1521',
                    p_sid:str='oratech',
                    p_name:str='oratech'):
    DJANGO_DB_NAME = p_name
    DJANGO_DB_USER = p_user
    DJANGO_DB_PWD = p_pwd
    DJANGO_DB_HOST = p_host
    DJANGO_DB_PORT = p_port
    try:
        if len(p_user) > 5:
            settings.configure(NAME=DJANGO_DB_NAME)
            settings.configure(USER=DJANGO_DB_USER)
            settings.configure(PASSWORD=DJANGO_DB_PWD)
            settings.configure(HOST=DJANGO_DB_HOST)
            settings.configure(PORT=DJANGO_DB_PORT)
    except:
        pass
    print('dbuser',settings.DATABASES)

if __name__ == '__main__':
    set_connection()
    print('dbuser',settings.DATABASES)