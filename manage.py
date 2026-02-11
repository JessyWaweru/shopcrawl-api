#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import socket

# --- START FORCE IPv4 PATCH ---
# This forces the app to ignore IPv6 addresses to prevent the 30s timeout on Render
try:
    original_getaddrinfo = socket.getaddrinfo
    def new_getaddrinfo(*args, **kwargs):
        res = original_getaddrinfo(*args, **kwargs)
        # Filter out any IPv6 results (AF_INET6)
        return [r for r in res if r[0] == socket.AF_INET]
    socket.getaddrinfo = new_getaddrinfo
except Exception:
    pass
# --- END FORCE IPv4 PATCH ---

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopcrawl_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()