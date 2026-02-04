from django.db import models
from django.contrib.auth.models import AbstractUser

# ==========================================
# USER MODEL
# ==========================================
class User(AbstractUser):
    email = models.EmailField(unique=True)
    password_digest = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# ==========================================
# VENDOR MODELS (Updated to match Seed.py)
# ==========================================

class Amazon(models.Model):
    link = models.URLField(default="https://amazon.com")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Matching your seed.py fields:
    days_to_ship = models.IntegerField(default=7) 
    review = models.DecimalField(max_digits=3, decimal_places=1, default=4.0) 
    product_location = models.CharField(max_length=100, default="Warehouse")

    def __str__(self):
        return f"Amazon: {self.price}"

class Jumia(models.Model):
    link = models.URLField(default="https://jumia.co.ke")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    days_to_ship = models.IntegerField(default=7)
    review = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    product_location = models.CharField(max_length=100, default="Warehouse")

    def __str__(self):
        return f"Jumia: {self.price}"

class Kilimall(models.Model):
    link = models.URLField(default="https://kilimall.co.ke")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    days_to_ship = models.IntegerField(default=7)
    review = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    product_location = models.CharField(max_length=100, default="Warehouse")

    def __str__(self):
        return f"Kilimall: {self.price}"

class Shopify(models.Model):
    link = models.URLField(default="#")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    days_to_ship = models.IntegerField(default=7)
    review = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    product_location = models.CharField(max_length=100, default="Warehouse")

    def __str__(self):
        return f"Shopify: {self.price}"

# ==========================================
# PRODUCT MODEL
# ==========================================

class Product(models.Model):
    name = models.CharField(max_length=255)
    
    # --- ADD THIS LINE ---
    about = models.TextField(blank=True, null=True) 
    
    description = models.TextField()
    image = models.TextField()      # <-- Unlimited length (Fixes the error)
    # ... rest of your fields (amazon, jumia, etc) ...
    
    # Relationships to vendors
    amazon = models.OneToOneField(Amazon, on_delete=models.SET_NULL, null=True, blank=True)
    jumia = models.OneToOneField(Jumia, on_delete=models.SET_NULL, null=True, blank=True)
    kilimall = models.OneToOneField(Kilimall, on_delete=models.SET_NULL, null=True, blank=True)
    shopify = models.OneToOneField(Shopify, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

# ==========================================
# USER PRODUCT (Cart/History)
# ==========================================

class UserProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"