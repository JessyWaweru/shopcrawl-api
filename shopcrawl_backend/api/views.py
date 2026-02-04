from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

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
    permission_classes = [AllowAny] 

# ==========================================
# USER VIEWSET
# ==========================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] # Critical for Sign Up / Reset Password

    # Custom Route: GET /users/:id/products
    @action(detail=True, methods=['get'], url_path='products')
    def get_all_user_products(self, request, pk=None):
        user = self.get_object() 
        user_products = UserProduct.objects.filter(user=user)
        serializer = UserProductSerializer(user_products, many=True)
        return Response(serializer.data)

# ==========================================
# SEARCH HISTORY
# ==========================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def search_history(request):
    user = request.user

    # 1. RETRIEVE HISTORY (GET)
    if request.method == 'GET':
        history = UserProduct.objects.filter(user=user).order_by('-date_added')[:11]
        serializer = UserProductSerializer(history, many=True)
        return Response(serializer.data)

    # 2. SAVE TO HISTORY (POST)
    elif request.method == 'POST':
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        # Avoid duplicates: delete old, add new to top
        UserProduct.objects.filter(user=user, product=product).delete()
        UserProduct.objects.create(user=user, product=product)
        
        return Response({"message": "Added to history"})

# ==========================================
# LOGIN FUNCTION (THE FIX)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # 1. Find User by Email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # 2. CHECK PASSWORD SECURELY
    # Use standard Django check_password() instead of checking password_digest
    if user.check_password(password):
        
        # 3. Generate Token
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        
        return Response({
            'token': token.key, 
            'user': serializer.data
        })
    else:
        return Response({'error': 'Invalid Password'}, status=status.HTTP_401_UNAUTHORIZED)