from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
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
# SEARCH HISTORY (New Feature)
# ==========================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def search_history(request):
    user = request.user

    # 1. RETRIEVE HISTORY (GET)
    if request.method == 'GET':
        # Get the last 11 items, newest first
        history = UserProduct.objects.filter(user=user).order_by('-date_added')[:11]
        serializer = UserProductSerializer(history, many=True)
        return Response(serializer.data)

    # 2. SAVE TO HISTORY (POST)
    elif request.method == 'POST':
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        # Avoid duplicates: If it's already in history, delete the old one so the new one goes to the top
        UserProduct.objects.filter(user=user, product=product).delete()

        # Create the new entry
        UserProduct.objects.create(user=user, product=product)
        
        return Response({"message": "Added to history"})

# ==========================================
# LOGIN FUNCTION (Matches React Frontend)
# ==========================================

# Add this import at the top

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = User.objects.filter(email=email).first()

    if user is None:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    db_digest = getattr(user, 'password_digest', None)

    if db_digest == password:
        # --- THE FIX: GENERATE TOKEN ---
        # Get or create a token for this user
        token, created = Token.objects.get_or_create(user=user)
        
        serializer = UserSerializer(user)
        
        # Return BOTH the user info AND the token
        return Response({
            'token': token.key, 
            'user': serializer.data
        })
    else:
        return Response({'error': 'Invalid Password'}, status=status.HTTP_401_UNAUTHORIZED)