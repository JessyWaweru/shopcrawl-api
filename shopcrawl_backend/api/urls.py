from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AmazonViewSet, JumiaViewSet, KilimallViewSet, ShopifyViewSet, 
    ProductViewSet, UserViewSet, 
    login_user, search_history  # <--- IMPORTED search_history
)

router = DefaultRouter()
router.register(r'amazons', AmazonViewSet)
router.register(r'jumia', JumiaViewSet)
router.register(r'kilimalls', KilimallViewSet)
router.register(r'shopifies', ShopifyViewSet)
router.register(r'products', ProductViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    # 1. SPECIFIC ROUTES FIRST
    # Login Route
    path('login/', login_user, name='login_user'),

    # Search History Route (New)
    path('history/', search_history, name='search_history'),

    # 2. GENERAL ROUTE SECOND (The Router)
    # Handles products, users, vendors, etc.
    path('', include(router.urls)),
]