from rest_framework import serializers
from .models import Amazon, Jumia, Kilimall, Shopify, Product, User, UserProduct

# ==========================================
# VENDOR SERIALIZERS
# These serializers handle the conversion of the specific vendor tables.
# ==========================================

class AmazonSerializer(serializers.ModelSerializer):
    # ModelSerializer is a shortcut that automatically creates a serializer 
    # based on the Model definition (fields, types, etc.)
    class Meta:
        model = Amazon
        # '__all__' is a magic keyword that tells Django to include 
        # every single field from the Amazon model in the JSON output.
        fields = '__all__'

class JumiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jumia
        fields = '__all__'

class KilimallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kilimall
        fields = '__all__'

class ShopifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopify
        fields = '__all__'

# ==========================================
# PRODUCT SERIALIZER
# This is the main object your API will likely return most often.
# ==========================================

class ProductSerializer(serializers.ModelSerializer):
    # Nested Serialization:
    # By default, Django would just give you the ID (e.g., "amazon": 1).
    # By declaring these variables here using the classes we defined above,
    # the JSON will include the FULL vendor object details nested inside the product.
    # It mimics Rails' `include: [:amazon, :jumia, ...]`
    amazon = AmazonSerializer(read_only=True)
    jumia = JumiaSerializer(read_only=True)
    kilimall = KilimallSerializer(read_only=True)
    shopify = ShopifySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

# ==========================================
# USER SERIALIZER
# ==========================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # We explicitly list fields here because we might want to exclude 
        # sensitive data like 'password_digest' in the future.
        fields = ['id', 'username', 'email', 'age', 'gender', 'admin', 'created_at']

# ==========================================
# USER PRODUCT (Cart/Wishlist) SERIALIZER
# ==========================================

class UserProductSerializer(serializers.ModelSerializer):
    # This serializer represents the link between a user and a product.
    
    # We can use 'depth' to automatically nest related objects.
    # depth = 1 means "go one level deep and show the actual Product data, 
    # not just the Product ID".
    class Meta:
        model = UserProduct
        fields = '__all__'
        depth = 1