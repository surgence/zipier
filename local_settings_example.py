DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'zipier',
        'USER': 'zipier',
        'PASSWORD': 'zipier',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

SECRET_KEY = 'makeitsecret'
