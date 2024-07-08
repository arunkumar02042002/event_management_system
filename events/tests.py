from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from rest_framework.test import APIClient, APITestCase
from rest_framework import status


from .models import Event, EventFeedback, Ticket
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


class BuyEventTicketViewTests(APITestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password123', email='user@user.user')
        self.client = APIClient()

        # Create an event
        self.event = Event.objects.create(
            title='Event 1',
            description='Description for event 1',
            start_time=timezone.now() + timedelta(days=2),
            created_by=self.user
        )

        self.invalid_slug = 'invalid-slug'
        self.url = reverse('buy-event-ticket', kwargs={'slug': self.event.slug})
        self.invalid_url = reverse('buy-event-ticket', kwargs={'slug': self.invalid_slug})

    def test_book_ticket_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(Ticket.objects.filter(event=self.event, user=self.user).count(), 1)
        self.assertEqual(Event.objects.get(slug=self.event.slug).no_of_participants, 1)

    def test_book_ticket_as_unauthenticated_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Ticket.objects.filter(event=self.event, user=self.user).count(), 0)
        self.assertEqual(Event.objects.get(slug=self.event.slug).no_of_participants, 0)

    def test_book_ticket_invalid_slug(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Invalid slug field')
        self.assertEqual(Ticket.objects.filter(event=self.event, user=self.user).count(), 0)

    def test_book_ticket_event_starting_soon(self):
        self.client.force_authenticate(user=self.user)
        self.event.start_time = timezone.now() + timedelta(minutes=59)
        self.event.save()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Booking time has been ended for this event.')
        self.assertEqual(Ticket.objects.filter(event=self.event, user=self.user).count(), 0)

    def test_book_ticket_already_booked(self):
        self.client.force_authenticate(user=self.user)
        Ticket.objects.create(event=self.event, user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'You have already booked your ticket')
        self.assertEqual(Ticket.objects.filter(event=self.event, user=self.user).count(), 1)


class MyTicketViewTests(APITestCase):

    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username='testuser1', password='password123', email="user1@email.com")
        self.user2 = User.objects.create_user(username='testuser2', password='password123', email="user2@email.com")

        self.client = APIClient()
        
        # Create events
        self.event1 = Event.objects.create(
            title='Event 1',
            description='Description for event 1',
            start_time=timezone.now() + timedelta(days=2),
            created_by=self.user1
        )
        self.event2 = Event.objects.create(
            title='Event 2',
            description='Description for event 2',
            start_time=timezone.now() + timedelta(days=2),
            created_by=self.user2
        )

        # Create tickets
        self.ticket1 = Ticket.objects.create(event=self.event1, user=self.user1)
        self.ticket2 = Ticket.objects.create(event=self.event2, user=self.user1)
        self.ticket3 = Ticket.objects.create(event=self.event1, user=self.user2)

        self.url = reverse('my-tickets')

    def test_retrieve_tickets_success(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['payload']['tickets']), 2)  # User 1 has 2 tickets

    def test_retrieve_tickets_for_user2(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['payload']['tickets']), 1)  # User 2 has 1 ticket

    def test_retrieve_tickets_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EventFeedbackListCreateViewTests(APITestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='testuser1', password='password123', email="user1@email.com")
        self.user2 = User.objects.create_user(username='testuser2', password='password123', email="user2@email.com")

        self.client = APIClient()
        
        # Create event
        self.event = Event.objects.create(
            title='Event 1',
            description='Description for event 1',
            start_time=timezone.now() + timedelta(days=2),
            slug='event-1',
            created_by=self.user1
        )

        # Create tickets
        self.ticket1 = Ticket.objects.create(event=self.event, user=self.user1)
        self.ticket2 = Ticket.objects.create(event=self.event, user=self.user2)

        # Create feedback
        self.feedback1 = EventFeedback.objects.create(
            event=self.event, user=self.user1, feedback="Great event!"
        )

        self.url = reverse('feedback-list-create', kwargs={'slug': 'event-1'})

    def test_retrieve_feedbacks_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['payload']['feedbacks']), 1)

    def test_submit_feedback_success(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'feedback': 'Amazing event!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['payload']['feedback']['feedback'], 'Amazing event!')

    def test_invalid_event_slug(self):
        invalid_url = reverse('feedback-list-create', kwargs={'slug': 'invalid-slug'})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Invalid slug field.')

    def test_submit_feedback_not_participant(self):
        self.client.force_authenticate(user=self.user1)
        new_event = Event.objects.create(
            title='Event 2',
            description='Description for event 2',
            start_time=timezone.now() + timedelta(days=2),
            slug='event-2',
            created_by=self.user2
        )
        new_url = reverse('feedback-list-create', kwargs={'slug': 'event-2'})
        data = {
            'feedback': 'Good event!'
        }
        response = self.client.post(new_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'You are not a participant of that event.')

    def test_submit_feedback_unauthenticated(self):
        data = {
            'feedback': 'Nice event!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_feedback_invalid_data(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'feedback': ''  # Invalid feedback (empty)
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('feedback', response.data['payload']['errors'])


class OraganizerEventListTests(APITestCase):

    def setUp(self):
        # Create users
        self.organizer = User.objects.create_user(username='organizer', password='password123', email="organizer@organizer.organizer", role=UserTypeChoices.ORGANIZER)
        self.admin = User.objects.create_superuser(username='admin', password='password123', email="admin@admin.admin")
        self.user = User.objects.create_user(username='user', password='password123', email="user@user.user")

        self.client = APIClient()

        # Create events
        self.event1 = Event.objects.create(
            title='Event 1',
            description='Description for event 1',
            start_time=timezone.now() + timedelta(days=2),
            slug='event-1',
            created_by=self.organizer
        )
        self.event2 = Event.objects.create(
            title='Event 2',
            description='Description for event 2',
            start_time=timezone.now() + timedelta(days=2),
            slug='event-2',
            created_by=self.organizer
        )
        self.event3 = Event.objects.create(
            title='Event 3',
            description='Description for event 3',
            start_time=timezone.now() + timedelta(days=2),
            slug='event-3',
            created_by=self.admin
        )

        self.url = reverse('organizer-events', kwargs={'username': 'organizer'})

    def test_retrieve_organizer_events_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['payload']['total_events'], 2)
        self.assertEqual(len(response.data['payload']['events']), 2)

    def test_organizer_not_found(self):
        url = reverse('organizer-events', kwargs={'username': 'nonexistent_organizer'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'No organizer with that username found.')

    def test_user_is_not_organizer_or_admin(self):
        url = reverse('organizer-events', kwargs={'username': 'user'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'No organizer with that username found.')