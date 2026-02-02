from django.db import models

class Amazon(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    days_to_ship = models.IntegerField(null=True, blank=True)
    review = models.IntegerField(null=True, blank=True)
    product_location = models.CharField(max_length=255, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Amazon Item {self.id}"

class Jumia(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    days_to_ship = models.IntegerField(null=True, blank=True)
    review = models.IntegerField(null=True, blank=True)
    product_location = models.CharField(max_length=255, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Jumia Item {self.id}"

class Kilimall(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    days_to_ship = models.IntegerField(null=True, blank=True)
    review = models.IntegerField(null=True, blank=True)
    product_location = models.CharField(max_length=255, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Kilimall Item {self.id}"

class Shopify(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    days_to_ship = models.IntegerField(null=True, blank=True)
    review = models.IntegerField(null=True, blank=True)
    product_location = models.CharField(max_length=255, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shopify Item {self.id}"

# --- Main Product Model ---

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=500, null=True, blank=True) # Assuming URL string
    about = models.CharField(max_length=255, null=True, blank=True)
    
    # Foreign Keys to Vendors
    # Rails 'belongs_to' becomes Django 'ForeignKey'
    # on_delete=models.CASCADE means if the Amazon entry is deleted, this product is also deleted.
    amazon = models.ForeignKey(Amazon, on_delete=models.CASCADE)
    shopify = models.ForeignKey(Shopify, on_delete=models.CASCADE)
    jumia = models.ForeignKey(Jumia, on_delete=models.CASCADE)
    kilimall = models.ForeignKey(Kilimall, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# --- User & Join Table ---

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_digest = models.CharField(max_length=255) # Storing the hash
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    admin = models.BooleanField(default=False)
    
    # This creates the relationship "User has many Products"
    # through the custom table below
    products = models.ManyToManyField(Product, through='UserProduct')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class UserProduct(models.Model):
    """
    This corresponds to your 'users_products' table.
    It links a User and a Product together (likely a cart or wishlist).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_products' # Keeps the table name identical to your old one