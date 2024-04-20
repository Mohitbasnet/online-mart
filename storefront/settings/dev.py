from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-ojjn#tpy@z@q*+&0#j4j0vd-9cme@@503yd=-w^docwlu5u#0%'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'Loveufather@123'
    }
}