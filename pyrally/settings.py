from os import environ

RALLY_USERNAME = environ.get('RALLY_USERNAME')
RALLY_PASSWORD = environ.get('RALLY_PASSWORD')

BASE_URL = 'https://rally1.rallydev.com/'


try:
    from local_settings import *
except ImportError:
    pass
