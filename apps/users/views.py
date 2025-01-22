from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, TemplateView
from apps.users.models import University, OTP
from apps.users.forms import SignUpForm, LoginForm
from core.services.otp_service import OTPService
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from apps.clubs.models import Club
from django.db.models import Q

User = get_user_model()


def home(request):
    # Sample data for featured clubs
    featured_clubs = [
        {
            'id': 1,
            'name': 'Tech Innovators',
            'description': 'Exploring cutting-edge technology and innovation',
            'member_count': 156,
            'image_url': 'https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&q=80&w=1600',
        },
        {
            'id': 2,
            'name': 'Art Society',
            'description': 'Express yourself through various art forms',
            'member_count': 89,
            'image_url': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=1600',
        },
        {
            'id': 3,
            'name': 'Debate Club',
            'description': 'Sharpen your critical thinking and speaking skills',
            'member_count': 124,
            'image_url': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&q=80&w=1600',
        },
    ]
    upcoming_events = [
        {
            'id': 1,
            'name': 'Tech Workshop 2024',
            'description': 'Learn about the latest technologies and their applications',
            'date': '2024-04-15',
            'image_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&q=80&w=1600',
            'attendees_count': 45,
        },
        # Add more events...
    ]
    
    ongoing_events = [
        {
            'id': 2,
            'name': 'Art Exhibition',
            'description': 'Showcasing student artwork from various mediums',
            'image_url': 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&q=80&w=1600',
            'attendees_count': 78,
        },
        # Add more events...
    ]
    
    past_events = [
        {
            'id': 3,
            'name': 'Debate Championship',
            'description': 'Annual inter-university debate competition',
            'date': '2024-02-20',
            'image_url': 'https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&q=80&w=1600',
            'attendees_count': 120,
        },
        # Add more events...
    ]
    
    return render(request, 'home.html', {
        'featured_clubs': featured_clubs,
        'upcoming_events': upcoming_events,
        'ongoing_events': ongoing_events,
        'past_events': past_events,
    })

class SignUpView(View):
    template_name = 'signup.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.is_email_verified:
            return redirect('home')
        form = SignUpForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated and request.user.is_email_verified:
            return redirect('home')

        form = SignUpForm(request.POST)
        email = form.data.get('email')

        # Check if user exists
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if not existing_user.is_email_verified:
                # User exists but email not verified - resend OTP
                # save the email and purpose in sesssion
                request.session['otp_email'] = email
                request.session['otp_purpose'] = 'VERIFY'
                send_otp_view = SendOtpView()
                response = send_otp_view.post(request)
                messages.info(request, "Account already exists. Please verify your email.")
                return redirect('users:verify_email')
            else:
                # User exists and is verified
                messages.error(request, "An account with this email already exists.")
                return render(request, self.template_name, {'form': form})

        if form.is_valid():
            domain = email.split('@')[-1]
            try:
                university = University.objects.get(domain=domain)
            except University.DoesNotExist:
                messages.error(request, "Invalid university email domain.")
                return render(request, self.template_name, {'form': form})

            user = form.save(commit=False)
            user.university = university
            user.username = email
            user.save()
            form.save_m2m()

            # Send OTP for new user
            request.session['otp_email'] = email
            request.session['otp_purpose'] = 'VERIFY'
            send_otp_view = SendOtpView()
            response = send_otp_view.post(request)
            messages.success(request, "Please check your email to verify your account.")
            return redirect('users:verify_email')

        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {'form': form})


class SendOtpView(View):
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request):
        email = request.session.get('otp_email')
        purpose = request.session.get('otp_purpose', 'VERIFY')

        if not email or not purpose:
            return JsonResponse({'error': 'No OTP process found in session.'}, status=400)

        try:
            user = User.objects.get(email=email)
            otp_service = OTPService(user, purpose)
            otp_service.send_otp()
            return JsonResponse({'message': 'OTP sent successfully.'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class VerifyOtpView(View):
    template_name = 'verify_email.html'

    def get(self, request, email=None):
        if request.user.is_authenticated and request.user.is_email_verified:
            return redirect('home')  # Redirect verified users to home
        try:
            email = request.session.get('otp_email')
            purpose = request.session.get('otp_purpose', 'VERIFY')
            if not email or not purpose:
                return redirect('users:login')
        except Exception:
            # Log the exception for debugging purposes if needed
            return redirect('users:login')  # Ensure a fallback redirect

        # If the session data exists, render the template
        return render(request, self.template_name, {'email': email, 'purpose': purpose})

    def post(self, request):
        email = request.session.get('otp_email')
        otp = request.POST.get('otp')
        purpose = request.session.get('otp_purpose', 'VERIFY')

        try:
            user = User.objects.get(email=email)
            otp_service = OTPService(user, purpose)
            is_valid, message = otp_service.verify(otp)

            if is_valid:
                if purpose == 'VERIFY':
                    user.is_email_verified = True
                    user.save()
                    messages.success(request, "Email verified successfully. You can now log in.")
                    return redirect('users:login')
                # Handle other purposes (password reset, etc.) here

            messages.error(request, message)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
        except ValidationError as e:
            messages.error(request, str(e))

        return render(request, self.template_name, {'email': email, 'purpose': purpose})

class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_email_verified:
                return redirect('home')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            if request.user.is_email_verified:
                return redirect('home')
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_email_verified:
                    login(request, user)
                    messages.success(request, "Logged in successfully.")
                    return redirect('home')
                else:
                    # Save details in session and resend OTP
                    request.session['otp_email'] = email
                    request.session['otp_purpose'] = 'VERIFY'
                    otp_service = OTPService(user, 'VERIFY')
                    otp_service.send_otp()
                    messages.info(request, "Please check your email to verify your account.")
                    return redirect('users:verify_email')
            else:
                messages.error(request, "Invalid email or password.")
        return render(request, self.template_name, {'form': form})

class LogoutView(View):
    def get(self, request):
        if not request.user.is_authenticated:  # Prevent access if user is not logged in
            messages.error(request, "You are not logged in.")
            return redirect('users:login')
        logout(request)
        messages.success(request, "Logged out successfully.")
        return redirect('home')
    
    
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Demo data
        clubs_data = [
            {
                'id': 1,
                'name': 'Tech Innovation Hub',
                'description': 'A space for tech enthusiasts to collaborate on cutting-edge projects',
                'image_url': 'https://images.unsplash.com/photo-1531482615713-2afd69097998',
                'status': 'active',
                'member_count': 156,
                'category': 'tech',
                'created_at': (timezone.now() - timedelta(days=30)).isoformat()
            },
            {
                'id': 2,
                'name': 'Photography Society',
                'description': 'Capturing moments and sharing stories through the lens',
                'image_url': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32',
                'status': 'active',
                'member_count': 89,
                'category': 'arts',
                'created_at': (timezone.now() - timedelta(days=15)).isoformat()
            }
        ]

        events_data = {
            'upcoming': [
                {
                    'id': 1,
                    'name': 'AI Workshop 2024',
                    'club_name': 'Tech Innovation Hub',
                    'date': '2024-03-20',
                    'image_url': 'https://images.unsplash.com/photo-1552664730-d307ca884978',
                    'location': 'Main Auditorium',
                    'participants': 45
                }
            ],
            'ongoing': [],
            'past': []
        }

        stats = {
            'joined_clubs_count': 5,
            'upcoming_events_count': len(events_data['upcoming']),
            'leadership_roles_count': 2,
            'new_notifications_count': 3
        }

        dashboard_data = {
            'clubs': clubs_data,
            'events': events_data,
            'stats': stats
        }

        context['dashboard_data'] = json.dumps(dashboard_data).replace('</script>', '<\\/script>')  # Pass JSON to the template
        context.update(stats)  # Pass stats as individual variables
        return context
    
class UserSearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        club_id = request.GET.get('club')
        
        if len(query) < 2:
            return JsonResponse({'results': []})
            
        club = get_object_or_404(Club, id=club_id)
        
        users = User.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query),
            university=request.user.university
        ).exclude(
            clubs=club
        )[:10]
        
        results = [{
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'avatar_url': f"https://ui-avatars.com/api/?name={user.first_name}+{user.last_name}&background=random"
        } for user in users]
        
        return JsonResponse({'results': results})