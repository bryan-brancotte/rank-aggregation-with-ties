"""
WSGI config for rnt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

basedir = os.path.dirname(os.path.dirname(__file__))
import sys
sys.path.insert(0, basedir)
sys.path.insert(0,'/opt/ibm/ILOG/CPLEX_Studio128/cplex/python/3.5/x86-64_linux')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rnt.settings")

application = get_wsgi_application()
