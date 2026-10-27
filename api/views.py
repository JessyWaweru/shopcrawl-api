from rest_framework import viewsets, status, filters  # <--- filters used for Search and Ordering
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from django.utils.crypto import constant_time_compare

from .models import Amazon, Jumia, Kilimall, Shopify, Product, User, UserProduct
from .serializers import (
    AmazonSerializer, JumiaSerializer, KilimallSerializer, ShopifySerializer, 
    ProductSerializer, UserSerializer, UserProductSerializer
)
from .permissions import IsAdminOrReadOnly, IsSelfOrAdmin, is_admin

# ==========================================
# VENDOR VIEWSETS
# ==========================================

class AmazonViewSet(viewsets.ModelViewSet):
    queryset = Amazon.objects.all()
    serializer_class = AmazonSerializer
    permission_classes = [IsAdminOrReadOnly]

class JumiaViewSet(viewsets.ModelViewSet):
    queryset = Jumia.objects.all()
    serializer_class = JumiaSerializer
    permission_classes = [IsAdminOrReadOnly]

class KilimallViewSet(viewsets.ModelViewSet):
    queryset = Kilimall.objects.all()
    serializer_class = KilimallSerializer
    permission_classes = [IsAdminOrReadOnly]

class ShopifyViewSet(viewsets.ModelViewSet):
    queryset = Shopify.objects.all()
    serializer_class = ShopifySerializer
    permission_classes = [IsAdminOrReadOnly]

# ==========================================
# PRODUCT VIEWSET (With Search & SmartRank™)
# ==========================================

class ProductViewSet(viewsets.ModelViewSet):
    
    # API endpoint for viewing, searching, and sorting products.
    # DEFAULT SORTING: Uses the Actuarial SmartRank™ (risk_adjusted_score) descending.
    # SEARCH LOGIC: Uses Django REST Framework's SearchFilter to allow 
    # querying via '?search=keyword' on name and description fields.
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    # --- ENABLE SEARCH & ORDERING ---
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description'] 
    
    # Enable the API to accept ordering queries if the frontend wants to override,
    # but set the default ordering to our new actuarial score.
    ordering_fields = ['risk_adjusted_score', 'expected_value', 'name']
    ordering = ['-risk_adjusted_score']  # The '-' means descending order (highest score first)

# ==========================================
# USER VIEWSET
# ==========================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Sign up is open to everyone; every other action is limited to your own account.
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsSelfOrAdmin()]

    def get_queryset(self):
        if is_admin(self.request.user):
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)

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
# LOGIN FUNCTION (Secure Version)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # 1. Find User by Email
    user = User.objects.filter(email=email).first()

    # 2. CHECK PASSWORD SECURELY
    # Same reply for unknown email and wrong password, so accounts can't be guessed.
    if user and user.check_password(password):
        
        # 3. Generate Token
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        
        return Response({
            'token': token.key, 
            'user': serializer.data
        })
    else:
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

# ==========================================
# PASSWORD RESET (Recovery PIN)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def reset_password(request):
    email = request.data.get('email')
    pin = str(request.data.get('recovery_pin') or '')
    new_password = request.data.get('password')

    if not (email and pin and new_password):
        return Response({'error': 'Email, recovery PIN and new password are required.'},
                        status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not (user and pin_matches(user, pin)):
        return Response({'error': 'Email or recovery PIN is incorrect.'},
                        status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password reset successfully.'})

reset_password.cls.throttle_scope = 'password_reset'


def pin_matches(user, pin):
    stored = user.recovery_pin or ''
    try:
        identify_hasher(stored)
    except ValueError:
        # Older accounts saved the PIN in plain text: check it, then upgrade it to a hash.
        if stored and constant_time_compare(stored, pin):
            user.recovery_pin = make_password(pin)
            return True
        return False
    return check_password(pin, stored)
