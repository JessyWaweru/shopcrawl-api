from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Product

# ==========================================
# 1. AUTHENTICATION TESTS
# ==========================================
class AuthTests(APITestCase):

    def test_signup_creates_user(self):
        """Test that a new user is created successfully."""
        url = reverse('user-list') 
        data = {
            'username': 'test@example.com', # <--- ADDED THIS (Required by API)
            'email': 'test@example.com',
            'password': 'StrongPassword1!',
            'password_confirmation': 'StrongPassword1!',
            'recovery_pin': '1234'
        }
        response = self.client.post(url, data, format='json')
        
        # If this fails, print the error to see exactly why
        if response.status_code != 201:
            print(f"\n❌ SIGNUP ERROR: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_login_returns_token(self):
        """Test that valid credentials return a token."""
        User.objects.create_user(
            username='loginuser@test.com',
            email='loginuser@test.com',
            password='StrongPassword1!'
        )
        url = reverse('login_user')
        data = {'email': 'loginuser@test.com', 'password': 'StrongPassword1!'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

# ==========================================
# 2. PRODUCT SEARCH TESTS
# ==========================================
class ProductSearchTests(APITestCase):

    def setUp(self):
        """Create dummy products for search tests."""
        self.p1 = Product.objects.create(
            name="iPhone 13 Pro", 
            description="Latest Apple smartphone with pro camera."
        )
        self.p2 = Product.objects.create(
            name="Samsung Galaxy S21", 
            description="Android smartphone with great zoom."
        )
        self.p3 = Product.objects.create(
            name="Nike Air Max", 
            description="Running shoes."
        )

    def test_list_all_products(self):
        """Test retrieving full list."""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_search_returns_specific_product(self):
        """Test searching for 'iPhone'."""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'iPhone'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "iPhone 13 Pro")

    def test_search_returns_multiple_matches(self):
        """Test searching 'smartphone' finds both phones."""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'smartphone'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_returns_empty_for_no_match(self):
        """Test searching for nonsense returns nothing."""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'toaster'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)