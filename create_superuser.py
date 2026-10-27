import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopcrawl_backend.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Live admin login comes from environment variables (set them in the Render dashboard).
USERNAME = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not PASSWORD:
    print("DJANGO_SUPERUSER_PASSWORD not set; skipping superuser setup.")
else:
    user = User.objects.filter(username=USERNAME).first()
    if user is None:
        print(f"Creating superuser: {USERNAME}")
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    else:
        # Keeps the live password in sync with the environment variable.
        print(f"Superuser {USERNAME} exists; syncing password.")
        user.set_password(PASSWORD)
        user.save()
