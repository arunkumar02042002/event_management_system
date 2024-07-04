from django.shortcuts import render

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.generics import GenericAPIView

from .permission import IsOrganizerOrReadOnly, IsParticipantorEventOrganizer
from .models import Event, Ticket
from . import serializers as event_serialziers

# Create your views here.
class EventsListCreateApiView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly)
    queryset = Event.objects.all()
    serializer_class = event_serialziers.EventSerializer

class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, IsParticipantorEventOrganizer)
    queryset = Event.objects.all()
    lookup_field = 'slug'
    serializer_class = event_serialziers.EventSerializer