from rest_framework import serializers
from .models import Amazon, Jumia, Kilimall, Shopify, Product, User, UserProduct

# ==========================================
# 1. VENDOR SERIALIZERS
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
# 2. PRODUCT SERIALIZER (The Big Logic)
# ==========================================

class ProductSerializer(serializers.ModelSerializer):
    # READ-ONLY DATA
    amazon_data = serializers.SerializerMethodField()
    jumia_data = serializers.SerializerMethodField()
    kilimall_data = serializers.SerializerMethodField()
    shopify_data = serializers.SerializerMethodField()

    # WRITE-ONLY INPUTS
    # Added "reviews" fields for each vendor
    amazon_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    amazon_shipping = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    amazon_days = serializers.IntegerField(write_only=True, required=False)
    amazon_location = serializers.CharField(write_only=True, required=False)
    amazon_reviews = serializers.DecimalField(max_digits=3, decimal_places=1, write_only=True, required=False) # NEW

    jumia_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    jumia_shipping = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    jumia_days = serializers.IntegerField(write_only=True, required=False)
    jumia_location = serializers.CharField(write_only=True, required=False)
    jumia_reviews = serializers.DecimalField(max_digits=3, decimal_places=1, write_only=True, required=False) # NEW

    kilimall_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    kilimall_shipping = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    kilimall_days = serializers.IntegerField(write_only=True, required=False)
    kilimall_location = serializers.CharField(write_only=True, required=False)
    kilimall_reviews = serializers.DecimalField(max_digits=3, decimal_places=1, write_only=True, required=False) # NEW

    shopify_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    shopify_shipping = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    shopify_days = serializers.IntegerField(write_only=True, required=False)
    shopify_location = serializers.CharField(write_only=True, required=False)
    shopify_reviews = serializers.DecimalField(max_digits=3, decimal_places=1, write_only=True, required=False) # NEW

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'about', 'image', 
            'amazon_data', 'jumia_data', 'kilimall_data', 'shopify_data',
            'amazon_price', 'amazon_shipping', 'amazon_days', 'amazon_location', 'amazon_reviews',
            'jumia_price', 'jumia_shipping', 'jumia_days', 'jumia_location', 'jumia_reviews',
            'kilimall_price', 'kilimall_shipping', 'kilimall_days', 'kilimall_location', 'kilimall_reviews',
            'shopify_price', 'shopify_shipping', 'shopify_days', 'shopify_location', 'shopify_reviews',
        ]

    # --- GET DATA HELPERS ---
    def get_vendor_data(self, obj, vendor_name):
        if hasattr(obj, vendor_name) and getattr(obj, vendor_name):
            vendor = getattr(obj, vendor_name)
            return {
                "price": vendor.price,
                "rating": getattr(vendor, 'review', 0.0), # Maps 'review' from DB to 'rating' for frontend
                "shipping_cost": getattr(vendor, 'shipping_cost', 0.0),
                "shipping_days": getattr(vendor, 'days_to_ship', 7),
                "location": getattr(vendor, 'product_location', "Unknown")
            }
        return None

    def get_amazon_data(self, obj): return self.get_vendor_data(obj, 'amazon')
    def get_jumia_data(self, obj): return self.get_vendor_data(obj, 'jumia')
    def get_kilimall_data(self, obj): return self.get_vendor_data(obj, 'kilimall')
    def get_shopify_data(self, obj): return self.get_vendor_data(obj, 'shopify')

    # --- UPDATE HELPERS ---
    def update_vendor(self, vendor_obj, validated_data, prefix):
        has_updates = False
        if f'{prefix}_price' in validated_data:
            vendor_obj.price = validated_data[f'{prefix}_price']
            has_updates = True
        if f'{prefix}_shipping' in validated_data:
            vendor_obj.shipping_cost = validated_data[f'{prefix}_shipping']
            has_updates = True
        if f'{prefix}_days' in validated_data:
            vendor_obj.days_to_ship = validated_data[f'{prefix}_days']
            has_updates = True
        if f'{prefix}_location' in validated_data:
            vendor_obj.product_location = validated_data[f'{prefix}_location']
            has_updates = True
        # NEW: Update Review
        if f'{prefix}_reviews' in validated_data:
            vendor_obj.review = validated_data[f'{prefix}_reviews']
            has_updates = True
            
        if has_updates:
            vendor_obj.save()

    # --- CREATE LOGIC ---
    def create(self, validated_data):
        def extract_vendor(prefix):
            return {
                "price": validated_data.pop(f'{prefix}_price', None),
                "shipping_cost": validated_data.pop(f'{prefix}_shipping', 0),
                "days_to_ship": validated_data.pop(f'{prefix}_days', 7),
                "product_location": validated_data.pop(f'{prefix}_location', 'Warehouse'),
                "review": validated_data.pop(f'{prefix}_reviews', 0.0) # Extract Review
            }

        a_data = extract_vendor('amazon')
        j_data = extract_vendor('jumia')
        k_data = extract_vendor('kilimall')
        s_data = extract_vendor('shopify')

        amazon_obj = Amazon.objects.create(**a_data) if a_data['price'] else None
        jumia_obj = Jumia.objects.create(**j_data) if j_data['price'] else None
        kilimall_obj = Kilimall.objects.create(**k_data) if k_data['price'] else None
        shopify_obj = Shopify.objects.create(**s_data) if s_data['price'] else None

        product = Product.objects.create(
            amazon=amazon_obj, jumia=jumia_obj, kilimall=kilimall_obj, shopify=shopify_obj,
            **validated_data
        )
        return product

    # --- UPDATE LOGIC ---
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.about = validated_data.get('about', instance.about)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        def handle_vendor_update(vendor_instance, prefix, model_class):
            if vendor_instance:
                self.update_vendor(vendor_instance, validated_data, prefix)
            elif validated_data.get(f'{prefix}_price'):
                # Create new vendor if price provided
                new_vendor = model_class.objects.create(
                    price=validated_data.get(f'{prefix}_price'),
                    shipping_cost=validated_data.get(f'{prefix}_shipping', 0),
                    days_to_ship=validated_data.get(f'{prefix}_days', 7),
                    product_location=validated_data.get(f'{prefix}_location', 'Warehouse'),
                    review=validated_data.get(f'{prefix}_reviews', 0.0) # Save Review
                )
                setattr(instance, prefix, new_vendor)
                instance.save()

        handle_vendor_update(instance.amazon, 'amazon', Amazon)
        handle_vendor_update(instance.jumia, 'jumia', Jumia)
        handle_vendor_update(instance.kilimall, 'kilimall', Kilimall)
        handle_vendor_update(instance.shopify, 'shopify', Shopify)

        return instance
# ==========================================
# 3. USER SERIALIZERS (MUST BE HERE)
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