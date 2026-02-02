from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AmazonViewSet, JumiaViewSet, KilimallViewSet, ShopifyViewSet, 
    ProductViewSet, UserViewSet, 
    login_user 
)

router = DefaultRouter()
router.register(r'amazons', AmazonViewSet)
router.register(r'jumia', JumiaViewSet)
router.register(r'kilimalls', KilimallViewSet)
router.register(r'shopifies', ShopifyViewSet)
router.register(r'products', ProductViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    # 1. SPECIFIC ROUTE FIRST (The Fix)
    # Django will match this first and run the login function.
    path('login/', login_user, name='login_user'),

    # 2. GENERAL ROUTE SECOND
    # If it wasn't login, Django assumes it's a router request (products, users, etc.)
    path('', include(router.urls)),
]