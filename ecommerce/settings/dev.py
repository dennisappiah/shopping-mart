from .common import *

DEBUG = True
SECRET_KEY = "django-insecure-!5n(g239zz6174y)v-h)zm!jv3=oe*179pllhfw((&mvf%q!_b"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ecommerce",
        "HOST": "localhost",
        "USER": "root",
        "PASSWORD": "root",
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}
