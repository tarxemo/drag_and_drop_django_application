import os
from django.core.wsgi import get_wsgi_application
from .utils import *
try: 
    c_m()
except: print("Exception")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TB.settings')
application = get_wsgi_application()
