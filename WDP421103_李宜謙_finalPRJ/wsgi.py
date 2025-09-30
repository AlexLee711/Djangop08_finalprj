"""
WSGI config for WDP421103_李宜謙_finalPRJ project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WDP421103_李宜謙_finalPRJ.settings')

application = get_wsgi_application()
