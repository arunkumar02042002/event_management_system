from django.urls import path, include

from . import views as event_views

urlpatterns = [
    path('', view=event_views.EventsListCreateApiView.as_view(), name='event-list-create'),
    path('<slug:slug>', view=event_views.EventRetrieveUpdateDestroyAPIView.as_view(), name='event-retrieve-update-destroy'),
    path('<slug:slug>/buy-ticket', view=event_views.BuyEventTicketView.as_view(), name='buy-event-ticket'),
    path('<slug:slug>/feedbacks/', view=event_views.EventFeedbackListCreateView.as_view(), name="feedback-list-create"),
    path('my-tickets/', view=event_views.MyTicketView.as_view(), name='my-tickets'),
]
