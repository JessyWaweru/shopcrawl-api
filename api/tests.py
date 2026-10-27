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

# ==========================================
# 3. SECURITY TESTS
# ==========================================
class SecurityTests(APITestCase):

    def setUp(self):
        self.client.post(reverse('user-list'), {
            'username': 'alice@test.com', 'email': 'alice@test.com',
            'password': 'StrongPassword1!', 'recovery_pin': '4321',
        }, format='json')
        self.alice = User.objects.get(email='alice@test.com')
        self.bob = User.objects.create_user(username='bob@test.com', email='bob@test.com', password='BobPassword1!')

    def test_signup_cannot_self_grant_admin(self):
        self.client.post(reverse('user-list'), {
            'username': 'eve@test.com', 'email': 'eve@test.com',
            'password': 'StrongPassword1!', 'admin': True, 'admin_code': 'secret123',
        }, format='json')
        self.assertFalse(User.objects.get(email='eve@test.com').admin)

    def test_recovery_pin_is_hashed_and_hidden(self):
        self.assertNotEqual(self.alice.recovery_pin, '4321')
        self.client.force_authenticate(self.alice)
        response = self.client.get(reverse('user-detail', args=[self.alice.id]))
        self.assertNotIn('recovery_pin', response.data)

    def test_user_list_is_not_public(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_edit_another_user(self):
        self.client.force_authenticate(self.bob)
        response = self.client.patch(reverse('user-detail', args=[self.alice.id]), {'password': 'hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_only_admins_can_change_products(self):
        response = self.client.post(reverse('product-list'), {'name': 'Fake'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.bob)
        response = self.client.post(reverse('product-list'), {'name': 'Fake'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reset_password_with_pin(self):
        url = reverse('reset_password')
        bad = self.client.post(url, {'email': 'alice@test.com', 'recovery_pin': '0000', 'password': 'New1!'}, format='json')
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)
        good = self.client.post(url, {'email': 'alice@test.com', 'recovery_pin': '4321', 'password': 'NewPassword1!'}, format='json')
        self.assertEqual(good.status_code, status.HTTP_200_OK)
        self.alice.refresh_from_db()
        self.assertTrue(self.alice.check_password('NewPassword1!'))

    def test_legacy_plaintext_pin_still_works_and_gets_hashed(self):
        User.objects.filter(pk=self.bob.pk).update(recovery_pin='9999')
        response = self.client.post(reverse('reset_password'),
                                    {'email': 'bob@test.com', 'recovery_pin': '9999', 'password': 'NewPassword1!'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.bob.refresh_from_db()
        self.assertNotEqual(self.bob.recovery_pin, '9999')
