from django.urls import path
from . import views
app_name = 'users'
urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('otp/verify/', views.VerifyOtpView.as_view(), name='verify_email'),
    path('otp/send/', views.SendOtpView.as_view(), name='send_otp'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('search/', views.UserSearchView.as_view(), name='user_search'),
]
