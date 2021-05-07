"""
WSGI config for rnt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

basedir = os.path.dirname(os.path.dirname(__file__))
import sys
sys.path.insert(0, basedir)
sys.path.insert(0,'/opt/ibm/ILOG/CPLEX_Studio201/cplex/python/3.8/x86-64_linux')
sys.path.insert(0,'/home/pierre/workspace/rank-aggregation-with-ties/env/lib/python3.8/site-packages')

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rnt.settings")
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rnt.settings")
django.setup()

# os.environ["DJANGO_SETTINGS_MODULE"] = "rnt.settings"
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

