from Door.settings.base import *

INSTALLED_APPS += (
    'debug_toolbar',
)

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('DOOR_DB_NAME'),
            'USER': os.getenv('DOOR_DB_USER'),
            'PASSWORD': os.getenv('DOOR_DB_PASSWORD'),
            'HOST': os.getenv('DOOR_DB_HOST'),
            'PORT': os.getenv('DOOR_DB_PORT'),
        }
}