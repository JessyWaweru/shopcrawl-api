from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Amazon, Jumia, Kilimall, Shopify, Product, User, UserProduct
from .serializers import (
    AmazonSerializer, JumiaSerializer, KilimallSerializer, ShopifySerializer, 
    ProductSerializer, UserSerializer, UserProductSerializer
)

# ==========================================
# VENDOR VIEWSETS
# ==========================================

class AmazonViewSet(viewsets.ModelViewSet):
    queryset = Amazon.objects.all()
    serializer_class = AmazonSerializer

class JumiaViewSet(viewsets.ModelViewSet):
    queryset = Jumia.objects.all()
    serializer_class = JumiaSerializer

class KilimallViewSet(viewsets.ModelViewSet):
    queryset = Kilimall.objects.all()
    serializer_class = KilimallSerializer

class ShopifyViewSet(viewsets.ModelViewSet):
    queryset = Shopify.objects.all()
    serializer_class = ShopifySerializer

# ==========================================
# PRODUCT VIEWSET
# ==========================================

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# ==========================================
# USER VIEWSET (Includes Sign-Up Fix)
# ==========================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # --- FIX: FORCE PASSWORD SAVE ON SIGNUP ---
    def create(self, request, *args, **kwargs):
        """
        Custom Create method to ensure password is saved correctly.
        """
        # 1. Run standard validation
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 2. Extract password manually from the request
            # We look for 'password' OR 'password_digest'
            pwd = request.data.get('password') or request.data.get('password_digest')
            
            print(f"--- SIGNUP DEBUG ---")
            print(f"Email: {request.data.get('email')}")
            print(f"Password to save: '{pwd}'")

            # 3. SAVE with the password explicitly included
            # This prevents the field from being blank in the database
            serializer.save(password_digest=pwd)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Signup Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Custom Route: GET /users/:id/products
    @action(detail=True, methods=['get'], url_path='products')
    def get_all_user_products(self, request, pk=None):
        user = self.get_object() 
        user_products = UserProduct.objects.filter(user=user)
        serializer = UserProductSerializer(user_products, many=True)
        return Response(serializer.data)

# ==========================================
# LOGIN FUNCTION (Matches React Frontend)
# ==========================================

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    print(f"\n--- DEBUG LOGIN ATTEMPT ---")
    print(f"Email received:     '{email}'")
    print(f"Password received:  '{password}'")

    # 1. Find User
    user = User.objects.filter(email=email).first()

    if user is None:
        print("RESULT: User not found in database.")
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # 2. Get the stored password safely
    # We use getattr so if the field is missing, it returns None instead of crashing
    db_digest = getattr(user, 'password_digest', None)
    
    print(f"User found:         {user.username}")
    print(f"DB password_digest: '{db_digest}'")

    # 3. Compare them directly
    if db_digest == password:
        print("RESULT: MATCH! Logging in...")
        serializer = UserSerializer(user)
        return Response(serializer.data)
    else:
        print("RESULT: FAILED. Strings do not match.")
        return Response({'error': 'Invalid Password'}, status=status.HTTP_401_UNAUTHORIZED)