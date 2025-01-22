from django.urls import path
from apps.events.views import (
    EventsListView,
    EventDetailView,
    EventReactionView,
    EventReactorsView,
    EventShareView,
    EventParticipateView,
)

app_name = 'events'

urlpatterns = [
    path('', EventsListView.as_view(), name='events'),
    path('<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('<int:event_id>/react/', EventReactionView.as_view(), name='event_react'),
    path('<int:event_id>/reactors/', EventReactorsView.as_view(), name='event_reactors'),
    path('<int:event_id>/share/', EventShareView.as_view(), name='event_share'),
    path('<int:event_id>/participate/', EventParticipateView.as_view(), name='event_participate'),
]