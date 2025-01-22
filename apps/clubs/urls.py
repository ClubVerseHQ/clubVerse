import stat
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'clubs'

urlpatterns = [
    path('', views.ClubListView.as_view(), name='clubs'),
    path('<int:pk>/', views.ClubDetailUpdateView.as_view(), name='club_detail'),
    path('<int:pk>/members/', views.ClubMemberManagementView.as_view(), name='club_member_management'),
    path('<int:pk>/leave/', views.LeaveClubView.as_view(), name='leave_club'),
    path('<int:pk>/members/add/', views.AddClubMemberView.as_view(), name='add_member'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
