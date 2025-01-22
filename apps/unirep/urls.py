from django.urls import path
from . import views
app_name = 'unirep'
urlpatterns = [
    path('clubs/create/', views.ClubCreateView.as_view(), name='create_club'),
    path('clubs/<int:pk>/delete/', views.ClubDeleteView.as_view(), name='delete_club'),
    path('clubs/<int:pk>/change-details/', views.ClubChangeDetailsView.as_view(), name='change_club_details'),
    path('clubs/<int:pk>/appoint-gs/', views.AppointGSView.as_view(), name='appoint_gs'),
]

