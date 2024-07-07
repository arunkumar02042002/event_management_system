from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from django.db import transaction

from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from .permission import IsOrganizerOrReadOnly, IsParticipantorEventOrganizer
from .models import Event, Ticket, EventFeedback
from . import serializers as event_serialziers
from . import throttles as event_throttles


# Create your views here.
class EventsListCreateApiView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly)
    serializer_class = event_serialziers.EventSerializer

    def get_throttles(self):
        if self.request.method == 'POST':
            throttle_classes = [event_throttles.RestrictedThrottle]
        else:
            throttle_classes = [event_throttles.UnrestrictedThrottle]
        return [throttle() for throttle in throttle_classes]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "status":"success",
            "message":"Events successfully retrieved.",
            "payload": {'events' : [response.data]},
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Events successfully created.",
            "payload": {'events' : [response.data]},
        }, status=status.HTTP_201_CREATED)
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def get_queryset(self):
        return Event.objects.all().select_related('created_by')


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, IsParticipantorEventOrganizer)
    queryset = Event.objects.all()
    lookup_field = 'slug'
    serializer_class = event_serialziers.EventSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        user = request.user
        ticket = Ticket.objects.filter(user=user, event=instance).first()
        if ticket:
            booked = True
        else:
            booked = False
        return Response({
            "status":"success",
            "message":"Event Details Retrieved",
            "payload": {
                "booked":booked,
                "events":[serializer.data]
            }
        })
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "status":"sucsess",
            "message":"Event updated sucessfully!",
            "payload":{
                "event":response.data
            }
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({
            "status":"success",
            "message":"Event deleted Sucessfully!",
            "payload":{}
        }, status=response.status_code)

    def get_throttles(self):
        if self.request.method == 'GET':
            throttle_classes = [event_throttles.UnrestrictedThrottle]
        else:
            throttle_classes = [event_throttles.RestrictedThrottle]
        return [throttle() for throttle in throttle_classes]


class BuyEventTicketView(GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = event_serialziers.TicketSerializer
    throttle_scope = 'restricted'
    
    def post(self, request, slug, *args, **kwargs):
        event = Event.objects.filter(slug=slug).first()
        if not event:
            return Response({
                "status":"error",
                "message":"Invalid slug field",
                "payload":{}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if event.start_time < timezone.now()+timedelta(hours=1):
            return Response({
                "status":"error",
                "message":"Booking time has been ended for this event.",
                "payload":{}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user

        with transaction.atomic():
            ticket, created = Ticket.objects.get_or_create(event=event, user=user)

            if created:
                event.no_of_participants += 1
                event.save()

        if created:
            serializer = self.serializer_class(instance=ticket)
            return Response({
                "status":"success",
                "message":"Your ticket for that event has been booked.",
                "payload":serializer.data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "status":"error",
            "message":"You have already booked your ticket",
            "payload":{}
        }, status=status.HTTP_400_BAD_REQUEST)
    

class MyTicketView(ListAPIView):
    permission_classes = IsAuthenticated,
    serializer_class = event_serialziers.TicketSerializer
    throttle_scope  = 'unrestricted'

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            "status":"success",
            "message":"Tickets retrieved successfully!",
            "payload": serializer.data,
        }, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).select_related('user', 'event')
    

class EventFeedbackListCreateView(GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = event_serialziers.EventFeedbackSerializer

    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        event = Event.objects.filter(slug=slug).first()

        if not event:
            return Response({
                "status":"error",
                "message":"Invalid slug field.",
                "payload":{}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        feedbacks = EventFeedback.objects.filter(event=event).select_related('user')
        serializer = self.serializer_class(feedbacks, many=True)

        return Response({
            "status":"success",
            "message":"Feedbacks retrieved successfully.",
            "payload":{
                "feedbacks":serializer.data
            }
        }, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        event = Event.objects.filter(slug=slug).first()

        if not event:
            return Response({
                "status":"error",
                "message":"Invalid slug field.",
                "payload":{}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the user a participant of the event
        user = request.user
        ticket = Ticket.objects.filter(event=event, user=user)

        if not ticket:
            return Response({
                "status":"error",
                "message":"You are not a participant of that event.",
                "payload":{}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        requested_data = request.data
        print(requested_data)
        serializer = self.serializer_class(data=requested_data)

        if serializer.is_valid() is False:
            return Response({
                "status":"error",
                "message":"Please correct the following errors.",
                "payload":{
                    "errors":serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        feedback = EventFeedback.objects.create(user=user, event=event, **validated_data)

        serializer = self.serializer_class(feedback)
        return Response({
            "status":"success",
            "message":"Your feedback has been submitted.",
            "payload": {
                "feedback":serializer.data
            }
        }, status=status.HTTP_201_CREATED)
