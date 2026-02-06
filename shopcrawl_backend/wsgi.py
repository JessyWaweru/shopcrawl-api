"""
WSGI config for shopcrawl_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# shopcrawl_backend/wsgi.py

import os
import socket

# --- START FORCE IPv4 PATCH ---
# This forces the app to ignore IPv6 addresses to prevent the 30s timeout on Render
original_getaddrinfo = socket.getaddrinfo

def new_getaddrinfo(*args, **kwargs):
    res = original_getaddrinfo(*args, **kwargs)
    # Filter out any IPv6 results (AF_INET6)
    return [r for r in res if r[0] == socket.AF_INET]

socket.getaddrinfo = new_getaddrinfo
# --- END FORCE IPv4 PATCH ---

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopcrawl_backend.settings')

application = get_wsgi_application()