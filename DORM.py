import os
import django
from django.conf import settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings.configure(
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join('db.sqlite3'),
        }
    },
    INSTALLED_APPS=[
        'schoold.apps.SchooldConfig',
    ]
)
django.setup()