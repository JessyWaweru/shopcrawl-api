from rest_framework import serializers
from .models import Amazon, Jumia, Kilimall, Shopify, Product, User, UserProduct

# ==========================================
# VENDOR SERIALIZERS
# ==========================================

class AmazonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amazon
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
# PRODUCT SERIALIZER (The Translator)
# ==========================================

class ProductSerializer(serializers.ModelSerializer):
    # These fields will hold the structured data for the frontend table
    amazon_data = serializers.SerializerMethodField()
    jumia_data = serializers.SerializerMethodField()
    kilimall_data = serializers.SerializerMethodField()
    shopify_data = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'image', 
            'amazon_data', 'jumia_data', 'kilimall_data', 'shopify_data'
        ]

    # --- Helper Logic to Map Database Fields to Frontend Names ---
    def get_vendor_data(self, obj, vendor_name):
        if hasattr(obj, vendor_name) and getattr(obj, vendor_name):
            vendor = getattr(obj, vendor_name)
            return {
                "price": vendor.price,
                
                # TRANSLATION 1: DB 'review' -> Frontend 'rating'
                "rating": getattr(vendor, 'review', 4.0), 
                
                "shipping_cost": getattr(vendor, 'shipping_cost', 0.0),
                
                # TRANSLATION 2: DB 'days_to_ship' -> Frontend 'shipping_days'
                "shipping_days": getattr(vendor, 'days_to_ship', 7),
                
                "location": getattr(vendor, 'product_location', "Unknown")
            }
        return None

    def get_amazon_data(self, obj): return self.get_vendor_data(obj, 'amazon')
    def get_jumia_data(self, obj): return self.get_vendor_data(obj, 'jumia')
    def get_kilimall_data(self, obj): return self.get_vendor_data(obj, 'kilimall')
    def get_shopify_data(self, obj): return self.get_vendor_data(obj, 'shopify')

# ==========================================
# USER SERIALIZERS
# ==========================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': False},
            'password_digest': {'write_only': False}
        }

class UserProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
    class Meta:
        model = UserProduct
        fields = ['id', 'user', 'product', 'date_added']