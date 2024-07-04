from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import Event
from authentication.choices import UserTypeChoices

from rest_framework.test import APIClient, APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

User = get_user_model()

class EventModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test_password', is_active=True, role=UserTypeChoices.ORGANIZER)
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            location="Test Location",
            start_time=timezone.now() + timedelta(days=1),
            created_by=self.user
        )

    def test_event_creation(self):
        self.assertEqual(self.event.title, "Test Event")
        self.assertEqual(self.event.description, "Test Description")
        self.assertEqual(self.event.location, "Test Location")
        self.assertEqual(self.event.created_by, self.user)
        self.assertTrue(self.event.slug)

    def test_event_string_representation(self):
        self.assertEqual(str(self.event), "Test Event")

    def test_event_slug_creation(self):
        event = Event.objects.create(
            title="Another Event",
            description="Another Description",
            location="Another Location",
            start_time=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        self.assertEqual(event.slug, "another-event")

    def test_event_start_time_default(self):
        event = Event.objects.create(
            title="Default Time Event",
            description="Default Time Description",
            location="Default Location",
            created_by=self.user
        )
        self.assertTrue(event.start_time > timezone.now())


class EventsListCreateApiViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test_password', role=UserTypeChoices.ORGANIZER, is_active=True)
        self.user2 = User.objects.create_user(username='otheruser', email='other@example.com', password='other_password', is_active=True)
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            location="Test Location",
            start_time=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        self.event_url = reverse('event-list-create')

    def test_list_events(self):
        response = self.client.get(self.event_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_event_authenticated_as_organizer(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Event',
            'description': 'New Description',
            'location': 'New Location',
            'start_time': timezone.now() + timedelta(days=2)
        }
        response = self.client.post(self.event_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 2)

    def test_create_event_authenticated_as_non_organizer(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            'title': 'Unauthorized Event',
            'description': 'Unauthorized Description',
            'location': 'Unauthorized Location',
            'start_time': timezone.now() + timedelta(days=2)
        }
        response = self.client.post(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), 1)

    def test_create_event_unauthenticated(self):
        data = {
            'title': 'Unauthorized Event',
            'description': 'Unauthorized Description',
            'location': 'Unauthorized Location',
            'start_time': timezone.now() + timedelta(days=2)
        }
        response = self.client.post(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), 1)

class EventRetrieveUpdateDestroyAPIViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.organizer = User.objects.create_user(username='organizer', email='organizer@example.com', password='test_password', role=UserTypeChoices.ORGANIZER, is_active=True)
        self.participant = User.objects.create_user(username='participant', email='participant@example.com', password='test_password', is_active=True)
        self.other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='other_password',  is_active=True)
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            location="Test Location",
            start_time=timezone.now() + timedelta(days=1),
            created_by=self.organizer
        )
        self.event_url = reverse('event-retrieve-update-destroy', kwargs={'slug': self.event.slug})

    def test_retrieve_event(self):
        response = self.client.get(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.event.title)

    def test_update_event_as_organizer(self):
        self.client.force_authenticate(user=self.organizer)
        data = {
            'title': 'Updated Event',
            'description': 'Updated Description',
            'location': 'Updated Location',
            'start_time': timezone.now() + timedelta(days=2)
        }
        response = self.client.put(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Event')

    def test_update_event_as_participant(self):
        self.client.force_authenticate(user=self.participant)
        data = {
            'title': 'Unauthorized Update',
            'description': 'Unauthorized Description',
            'location': 'Unauthorized Location',
            'start_time': timezone.now() + timedelta(days=2)
        }
        response = self.client.put(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.event.refresh_from_db()
        self.assertNotEqual(self.event.title, 'Unauthorized Update')

    def test_update_event_as_unauthenticated_user(self):
        data = {
            'title': 'Unauthorized Update',
            'description': 'Unauthorized Description',
            'location': 'Unauthorized Location',
            'start_time': timezone.now() + timedelta(days=2)
        }
        response = self.client.put(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.event.refresh_from_db()
        self.assertNotEqual(self.event.title, 'Unauthorized Update')

    def test_delete_event_as_organizer(self):
        self.client.force_authenticate(user=self.organizer)
        response = self.client.delete(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(slug=self.event.slug).exists())
        response = self.client.get(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_event_as_participant(self):
        self.client.force_authenticate(user=self.participant)
        response = self.client.delete(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Event.objects.filter(slug=self.event.slug).exists())

    def test_delete_event_as_unauthenticated_user(self):
        response = self.client.delete(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Event.objects.filter(slug=self.event.slug).exists())