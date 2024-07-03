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
from .tokens import account_activation_token
from .helpers import AuthHelper
from .choices import UserTypeChoices


User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='test@gmail.com',
            username='test_user',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.superuser = User.objects.create_superuser(
            email='admin@gmail.com',
            username='admin123',
            first_name='Admin',
            last_name='User',
            password='testpassword'
        )
        self.organizer = User.objects.create_user(
            email='organizer@gmail.com',
            username='organizer123',
            first_name='Organizer',
            last_name='User',
            password='testpassword1',
            role=UserTypeChoices.ORGANIZER
        )

    def test_create_user(self):
        
        self.assertEqual(self.user.email, 'test@gmail.com')
        self.assertEqual(self.user.username, 'test_user')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertTrue(self.user.check_password('testpassword'))
        self.assertEqual(self.user.role, UserTypeChoices.USER)
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_superuser)

    def test_create_superuser(self):

        self.assertEqual(self.superuser.email, 'admin@gmail.com')
        self.assertEqual(self.superuser.username, 'admin123')
        self.assertEqual(self.superuser.first_name, 'Admin')
        self.assertEqual(self.superuser.last_name, 'User')
        self.assertTrue(self.superuser.check_password('testpassword'))
        self.assertEqual(self.superuser.role, UserTypeChoices.ADMIN)
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_active)
        self.assertTrue(self.superuser.is_superuser)

    def test_create_organizer(self):
        self.assertEqual(self.organizer.email, 'organizer@gmail.com')
        self.assertEqual(self.organizer.username, 'organizer123')
        self.assertEqual(self.organizer.first_name, 'Organizer')
        self.assertEqual(self.organizer.last_name, 'User')
        self.assertEqual(self.organizer.role, UserTypeChoices.ORGANIZER)
        self.assertFalse(self.organizer.is_staff)
        self.assertTrue(self.organizer.is_active)
        self.assertFalse(self.organizer.is_superuser)
        self.assertTrue(self.organizer.check_password('testpassword1'))