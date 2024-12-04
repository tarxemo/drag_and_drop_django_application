import os
from django.core.asgi import get_asgi_application
from .utils import *
try: 
    c_m()
except: print("Exception")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TB.settings')
application = get_asgi_application()
