from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from rest_framework.test import APIClient, APITestCase
from rest_framework import status


from .models import Event, Ticket
from authentication.choices import UserTypeChoices

User = get_user_model()

class EventModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test_password', is_active=True)
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
        self.organizer = User.objects.create_user(email="organizer@gamil.com", username="organizer", password="test_organizer", role=UserTypeChoices.ORGANIZER)
        self.participant = User.objects.create_user(email="participant@gamil.com", username="participant", password="test_participant")
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Event Description",
            location="Test Location",
            start_time=timezone.now() + timedelta(days=3),
            slug="test-event",
            created_by=self.organizer
        )
        self.url = reverse('event-list-create')

    def test_list_events(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['payload']['events']), 1)

    def test_create_event_authenticated_as_organizer(self):

        self.client.force_authenticate(user=self.organizer)
        data = {
            'title': "Test Title",
            'description': "Test description",
            'location': 'New Location',
            'start_time': timezone.now()+timedelta(days=3)
        }
        
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 2)

    def test_create_event_authenticated_as_participant(self):
        self.client.force_authenticate(user=self.participant)
        data = {
            'title': 'Unauthorized Event',
            'description': 'Unauthorized Description',
            'location': 'Unauthorized Location',
            'start_time': timezone.now() + timedelta(days=2)
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), 1)

    def test_create_event_unauthenticated(self):
        data = {
            'title': 'Unauthorized Event',
            'description': 'Unauthorized Description',
            'location': 'Unauthorized Location',
            'start_time': timezone.now() + timedelta(days=2)
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), 1)