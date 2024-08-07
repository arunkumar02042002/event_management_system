# Django Imports
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode 
from django.contrib.auth.tokens import default_token_generator


# Rest Import
from rest_framework import status
from rest_framework.test import APIClient

# SimpleJWT Imports
from rest_framework_simplejwt.tokens import RefreshToken

# Local Imports
from authentication.tokens import account_activation_token
from authentication.choices import UserTypeChoices

import json


User = get_user_model()


class RegisterUserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('register-user')

    def test_signup_success(self):
        """
        Test successful user signup.
        """
        data = {
            'email': 'test@example.com',
            'password': 'test_password',
        }

        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.first()

        self.assertEqual(user.role, UserTypeChoices.USER)
        self.assertFalse(user.is_active)
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(check_password(password='test_password', encoded=user.password))

    def test_signup_existing_user(self):
        """
        Test signup with an existing user email.
        """
        existing_user = User.objects.create_user(email='existing@example.com', username='existing_user', password='existing_password')
        data = {
            'email': 'existing@example.com',
            'password': 'test_password',
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  # No new user should be created

    def test_signup_email_validation_errors(self):
        """
        Test signup with invalid data.
        """
        data = {
            'email': 'test.com',
            'password': 'test_password'
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_password_validation_errors(self):
        """
        Test signup with invalid data.
        """
        data = {
            'email': 'test@gmail.com',
            'password': ''
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegisterOrganizerViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('register-organizer')

    def test_signup_success(self):
        """
        Test successful user signup.
        """
        data = {
            'email': 'test@example.com',
            'password': 'test_password',
        }

        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.first()

        self.assertFalse(user.is_active)
        self.assertEqual(user.role, UserTypeChoices.ORGANIZER)
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(check_password(password='test_password', encoded=user.password))

    def test_signup_existing_user(self):
        """
        Test signup with an existing user email.
        """
        existing_user = User.objects.create_user(email='existing@example.com', username='existing_user', password='existing_password')
        data = {
            'email': 'existing@example.com',
            'password': 'test_password',
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  # No new user should be created

    def test_signup_email_validation_errors(self):
        """
        Test signup with invalid data.
        """
        data = {
            'email': 'test.com',
            'password': 'test_password'
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_password_validation_errors(self):
        """
        Test signup with invalid data.
        """
        data = {
            'email': 'test@gmail.com',
            'password': ''
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ActivateAccountViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.activate_url = reverse('activate-account')
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='test_password', is_active=False
        )

    def test_activate_account_success(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        data = {'uidb64': uidb64, 'token': token}
        response = self.client.post(self.activate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_account_invalid_uidb64(self):
        uidb64 = urlsafe_base64_encode(force_bytes(99999))  # Non-existent user id
        token = account_activation_token.make_token(self.user)
        data = {'uidb64': uidb64, 'token': token}
        response = self.client.post(self.activate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Activation link is invalid')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activate_account_invalid_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'invalid-token'
        data = {'uidb64': uidb64, 'token': token}
        response = self.client.post(self.activate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Activation link is invalid')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activate_account_missing_uidb64(self):
        token = account_activation_token.make_token(self.user)
        data = {'token': token}
        response = self.client.post(self.activate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Activation link is invalid')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activate_account_missing_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        data = {'uidb64': uidb64}
        response = self.client.post(self.activate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Activation link is invalid')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='test@example.com',  password='test_password', is_active=True)

    def test_login_success_using_username(self):
        """
        Test successful login.
        """
        data = {
            'username_or_email': 'testuser',
            'password': 'test_password',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['payload'])

    def test_login_success_using_email(self):
        """
        Test successful login.
        """
        data = {
            'username_or_email': 'test@example.com',
            'password': 'test_password',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['payload'])

    def test_login_invalid_credentials(self):
        """
        Test login with invalid credentials.
        """
        data = {
            'username_or_email': 'testuser',
            'password': 'wrong_password',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        """
        Test login with inactive user.
        """
        # Deactivate the user
        self.user.is_active = False
        self.user.save()
        data = {
            'username_or_email': 'testuser',
            'password': 'test_password',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_no_user_found(self):
        """
        Test login with non-existent user.
        """
        data = {
            'username_or_email': 'nonexistentuser',
            'password': 'test_password',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserLogoutViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.logout_url = reverse('logout')
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test_password', is_active=True)
        self.refresh = str(RefreshToken.for_user(user=self.user))
        

    def test_logout_success(self):
        """
        Test successful logout.
        """
        
        data = {'refresh': self.refresh}
        self.client.force_authenticate(self.user)

        response = self.client.post(self.logout_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_all_devices(self):
        """
        Test logout from all devices.
        """
        data = {'all': True}
        self.client.force_authenticate(self.user)
        self.refresh_token = RefreshToken.for_user(self.user)

        response = self.client.post(self.logout_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_invalid_token(self):
        """
        Test logout with invalid refresh token.
        """
        data = {'refresh': 'invalid_refresh_token'}
        self.client.force_authenticate(self.user)
        response = self.client.post(self.logout_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_unauthenticated(self):
        """
        Test logout when user is not authenticated.
        """
        data = {'refresh': self.refresh}
        response = self.client.post(self.logout_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CustomTokenRefreshViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.refresh_url = reverse('get-refresh-token')
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test_password', is_active=True)
        # Create a refresh token for testing
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_refresh_token_success(self):
        """
        Test successful token refresh.
        """
        data = {'refresh': self.refresh_token}
        response = self.client.post(self.refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_refresh_inactive_user(self):
        """
        Test token refresh with inactive user.
        """
        # Deactivate the user
        self.user.is_active = False
        self.user.save()
        data = {'refresh': self.refresh_token}
        response = self.client.post(self.refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.change_password_url = reverse('change-password')
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test_password')

    def test_change_password_success(self):
        """
        Test successful password change.
        """
        data = {
            'old_password': 'test_password',
            'new_password': 'new_test_password',
            'confirm_password': 'new_test_password',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_incorrect_old_password(self):
        """
        Test changing password with incorrect old password.
        """
        data = {
            'old_password': 'incorrect_password',
            'new_password': 'new_test_password',
            'confirm_password': 'new_test_password',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_password_incorrect_confirm_password(self):
        """
        Test changing password with incorrect confirm password.
        """
        data = {
            'old_password': 'incorrect_password',
            'new_password': 'new_test_password',
            'confirm_password': 'new_test_password2',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password_reset_url = reverse('password-reset')
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test_password')

    def test_password_reset_success(self):
        """
        Test successful password reset.
        """
        data = {'email': 'test@example.com'}
        response = self.client.post(self.password_reset_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_password_reset_non_existent_email(self):
        """
        Test password reset with non-existent email.
        """
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.password_reset_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_for_inactive_user(self):
        """
        Test password reset with non-existent email.
        """
        self.user.is_active = False
        self.user.save()
        data = {'email': 'test@example.com'}
        response = self.client.post(self.password_reset_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test_password')
        self.reset_confirm_url = reverse('password-reset-confirm', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)), 'token': default_token_generator.make_token(self.user)})
        
    def test_password_reset_confirm_success(self):
        """
        Test successful password reset confirmation.
        """
        data = {'new_password': 'new_test_password', 'confirm_password':'new_test_password'}
        response = self.client.post(self.reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_password_reset_confirm_incorrect_confirm_password(self):
        """
        Test incorrect confirm_password field.
        """
        data = {'new_password': 'new_test_password', 'confirm_password':'incorrect_test_password'}
        response = self.client.post(self.reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_invalid_token(self):
        """
        Test password reset confirmation with invalid token.
        """
        # Generate an invalid token by modifying the user's token
        invalid_token = default_token_generator.make_token(User())
        invalid_reset_confirm_url = reverse('password-reset-confirm', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)), 'token': invalid_token})
        data = {'new_password': 'new_test_password', 'confirm_password':'new_test_password'}
        response = self.client.post(invalid_reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)