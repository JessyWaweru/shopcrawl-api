import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopcrawl_backend.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Change these to whatever you want your Live Admin login to be
USERNAME = "admin"
EMAIL = "admin@example.com"
PASSWORD = "complexpassword123" 

if not User.objects.filter(username=USERNAME).exists():
    print(f"Creating superuser: {USERNAME}")
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
else:
    print(f"Superuser {USERNAME} already exists.")