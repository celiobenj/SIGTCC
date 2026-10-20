"""Interface WSGI do SIGTCC (servidor web síncrono).

[infraestrutura da feature 001, sem US específica]
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigtcc.settings")

application = get_wsgi_application()
