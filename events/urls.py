from django.urls import path, include

from . import views as event_views

urlpatterns = [
    path('', view=event_views.EventsListCreateApiView.as_view(), name='event-list-create'),
    path('<slug:slug>', view=event_views.EventRetrieveUpdateDestroyAPIView.as_view(), name='event-retrieve-update-destroy')
]
