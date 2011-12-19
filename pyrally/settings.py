from os import environ

RALLY_USERNAME = environ.get('RALLY_USERNAME')
RALLY_PASSWORD = environ.get('RALLY_PASSWORD')


KANBAN_STATES = ['Defined',
                 'In Development',
                 'In RC review',
                 'Ready for QA',
                 'In QA Testing',
                 'Passed QA',
                 'Merged into Staging',
                 'Deployed',
                 ]

try:
    from local_settings import *
except ImportError:
    pass
