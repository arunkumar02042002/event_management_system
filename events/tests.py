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
            created_by=self.organizer
        )
        self.other_event = Event.objects.create(
            title="Star Meet",
            description="An event like never before",
            location="Delhi",
            start_time=timezone.now() + timedelta(days=2),
            created_by=self.organizer
        )
        self.third_event = Event.objects.create(
            title="Third Event",
            description="An event like never before",
            location="Ney Yourk",
            start_time=timezone.now() + timedelta(days=1),
            created_by=self.organizer
        )
        self.url = reverse('event-list-create')

    def test_list_events(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['payload']['events']), 3)

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
        self.assertEqual(Event.objects.count(), 4)

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
        self.assertEqual(Event.objects.count(), 3)

    def test_create_event_unauthenticated(self):
        data = {
            'title': 'Unauthorized Event',
            'description': 'Unauthorized Description',
            'location': 'Unauthorized Location',
            'start_time': timezone.now() + timedelta(days=2)
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), 3)

    def test_ordering_events_start_time_increasing(self):
        response = self.client.get(self.url, {'ordering': 'start_time'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertTrue(events[0]['start_time'] < events[1]['start_time'])
        self.assertTrue(events[1]['start_time'] < events[2]['start_time'])

    def test_ordering_events_start_time_decreasing(self):
        response = self.client.get(self.url, {'ordering': '-start_time'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertTrue(events[0]['start_time'] > events[1]['start_time'])
        self.assertTrue(events[1]['start_time'] > events[2]['start_time'])

    def test_ordering_events_created_at_increasing(self):
        response = self.client.get(self.url, {'ordering': 'created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertTrue(events[0]['created_at'] <= events[1]['created_at'])
        self.assertTrue(events[1]['created_at'] <= events[2]['created_at'])

    def test_ordering_events_created_at_decreasing(self):
        response = self.client.get(self.url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertTrue(events[0]['created_at'] >= events[1]['created_at'])
        self.assertTrue(events[1]['created_at'] >= events[2]['created_at'])

    def test_ordering_events_updated_at_increasing(self):
        response = self.client.get(self.url, {'ordering': 'updated_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertTrue(events[0]['updated_at'] <= events[1]['updated_at'])
        self.assertTrue(events[1]['updated_at'] <= events[2]['updated_at'])

    def test_ordering_events_updated_at_decreasing(self):
        response = self.client.get(self.url, {'ordering': '-updated_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertTrue(events[0]['updated_at'] >= events[1]['updated_at'])
        self.assertTrue(events[1]['updated_at'] >= events[2]['updated_at'])

    def test_ordering_events_id_decreasing(self):
        response = self.client.get(self.url, {'ordering': 'id'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertTrue(events[0]['id'] < events[1]['id'])
        self.assertTrue(events[1]['id'] < events[2]['id'])

    def test_ordering_events_id_decreasing(self):
        response = self.client.get(self.url, {'ordering': '-id'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertTrue(events[0]['id'] > events[1]['id'])
        self.assertTrue(events[1]['id'] > events[2]['id'])


    def test_searching_events(self):
        response = self.client.get(self.url, {'search': 'meet'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertEqual(len(events), 1)
        self.assertIn('meet', events[0]['title'].lower())

        response = self.client.get(self.url, {'search': 'event'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']
        self.assertEqual(len(events), 2)
        self.assertIn('event', events[0]['title'].lower())
        self.assertIn('event', events[1]['title'].lower())


    def test_filtering_events(self):
        response = self.client.get(self.url, {'start_time__gt': timezone.now() + timedelta(days=1)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']

        self.assertEqual(len(events), 2)
        self.assertTrue(events[0]['title'] in ['Star Meet', 'Test Event'])
        self.assertTrue(events[1]['title'] in ['Star Meet', 'Test Event'])

        response = self.client.get(self.url, {'start_time__lte': timezone.now() + timedelta(days=2)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = response.data['payload']['events']

        self.assertEqual(len(events), 2)
        self.assertTrue(events[0]['title'] in ['Star Meet', 'Third Event'])
        self.assertTrue(events[1]['title'] in ['Star Meet', 'Third Event'])



class EventRetrieveUpdateDestroyAPIViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.organizer = User.objects.create_user(username='organizer', email='organizer@example.com', password='test_password', role=UserTypeChoices.ORGANIZER, is_active=True)
        self.participant = User.objects.create_user(username='participant', email='participant@example.com', password='test_password', is_active=True)
        self.other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='other_password', is_active=True)
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
        event = response.data['payload']['event']
        self.assertEqual(event['title'], self.event.title)

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
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Event.objects.filter(slug=self.event.slug).exists())

    def test_delete_event_as_participant(self):
        self.client.force_authenticate(user=self.participant)
        response = self.client.delete(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Event.objects.filter(slug=self.event.slug).exists())

    def test_delete_event_as_unauthenticated_user(self):
        response = self.client.delete(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Event.objects.filter(slug=self.event.slug).exists())