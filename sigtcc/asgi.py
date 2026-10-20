"""Interface ASGI do SIGTCC.

[infraestrutura da feature 001, sem US específica]
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigtcc.settings")

application = get_asgi_application()
