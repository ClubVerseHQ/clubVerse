from django.views import View
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch
from apps.clubs.models import Club, ClubType, ClubRole, ClubMembership
from apps.clubs.forms import ClubMembershipForm, ClubForm
from django.contrib.auth import get_user_model
from apps.universities.models import Department
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
import json
User = get_user_model()

class ClubListView(ListView):
    model = Club
    template_name = 'clubs.html'
    context_object_name = 'clubs'
    paginate_by = 10

    def get_queryset(self):
        # Start with basic queryset filtered by university
        queryset = Club.objects.filter(
            is_active=True,
            department__university=self.request.user.university
        ).select_related('type', 'department').prefetch_related('members')

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Type filter functionality
        selected_type = self.request.GET.get('type', 'all')
        if selected_type != 'all':
            queryset = queryset.filter(type__name=selected_type)

        # Department filter functionality (only for 'dept' type clubs)
        selected_department = self.request.GET.get('department', 'all')
        if selected_department != 'all':
            queryset = queryset.filter(department_id=selected_department)

        # Sorting functionality
        selected_sort = self.request.GET.get('sort', 'newest')
        if selected_sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif selected_sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif selected_sort == 'members':
            queryset = queryset.annotate(num_members=Count('members')).order_by('-num_members')
        elif selected_sort == 'name':
            queryset = queryset.order_by('name')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        # Fetch club types for the user's university
        context['club_types'] = list(ClubType.objects.filter(
            clubs__department__university=self.request.user.university
        ).distinct().values('id', 'name'))
    
        # Fetch departments for the user's university
        departments_data = list(Department.objects.filter(
            university=self.request.user.university
        ).values('id', 'full_name', 'short_name'))
    
        # Prepare departments data for JSON serialization
        departments_json = [{'id': 'all', 'name': 'All Departments'}] + [
            {'id': dept['id'], 'name': dept['full_name']} for dept in departments_data
        ]
    
        context['departments'] = json.dumps(departments_json, cls=DjangoJSONEncoder)
        context['selected_type'] = self.request.GET.get('type', 'all')
        context['selected_department'] = self.request.GET.get('department', 'all')
        context['sort_by'] = self.request.GET.get('sort', 'newest')
        context['search_query'] = self.request.GET.get('search', '')
    
        # Serialize clubs data
        clubs_data = [
            {
                'id': club.id,
                'name': club.name,
                'description': club.description,
                'image_url': club.image.url if club.image else None,
                'type': club.type.name,
                'department_name': club.department.full_name if club.department else None,
                'department_id': club.department.id if club.department else None,
                'member_count': club.members.count(),
                'events_count': getattr(club, 'events', []).count(),  # Use getattr in case 'events' is not defined
                'created_at': club.created_at.isoformat(),
                'is_member': self.request.user in club.members.all()
            }
            for club in context['clubs']
        ]
        context['clubs_json'] = json.dumps(clubs_data, cls=DjangoJSONEncoder)
    
        return context


class ClubDetailUpdateView(LoginRequiredMixin, DetailView, UpdateView):
    model = Club
    form_class = ClubForm
    template_name = 'club_detail.html'
    context_object_name = 'club'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = self.get_object()

        # Get current user's membership and role
        try:
            user_membership = ClubMembership.objects.get(
                user=self.request.user,
                club=club
            )
            user_role = user_membership.role.name if user_membership.role else 'Member'
            is_member = True
        except ClubMembership.DoesNotExist:
            user_role = None
            is_member = False

        # Fetch all available roles
        available_roles = list(ClubRole.objects.all().values('id', 'name'))

        # Serialize club data
        club_data = {
            'id': club.id,
            'name': club.name,
            'description': club.description or "Welcome to our club! We are dedicated to fostering innovation and collaboration...",
            'image_url': club.image.url if club.image else None,
            'type': club.type.name,
            'department_name': club.department.full_name if club.department else None,
            'department_id': club.department.id if club.department else None,
            'member_count': club.members.count(),
            'events_count': getattr(club, 'events', []).count(),
            'created_at': club.created_at.isoformat(),
            'is_member': is_member,
            'user_role': user_role,
            'about': """
            Our club is committed to excellence in technology and innovation.
            We organize regular workshops, hackathons, and networking events.
            Join us to be part of an exciting journey of learning and growth!
            """
        }

        # Get members data
        members_data = [
            {
                'id': membership.user.id,
                'name': f"{membership.user.first_name} {membership.user.last_name}",
                'email': membership.user.email,
                'blacklisted': membership.blacklisted,
                'role': membership.role.name if membership.role else 'Member',
                'avatar_url': f"https://ui-avatars.com/api/?name={membership.user.first_name}+{membership.user.last_name}&background=random",
                'joined_at': membership.joined_at.strftime('%B %d, %Y')
            }
            for membership in club.memberships.select_related('user', 'role').all()
        ]

        # Recent activities data (can be fetched dynamically if needed)
        activities_data = [
            {
                'id': 1,
                'icon': 'user-plus',
                'title': 'New Member Joined',
                'description': 'Sarah Parker joined the club',
                'timestamp': '2 hours ago'
            },
            {
                'id': 2,
                'icon': 'calendar',
                'title': 'New Event Scheduled',
                'description': 'Tech Talk: Introduction to AI',
                'timestamp': '1 day ago'
            },
            {
                'id': 3,
                'icon': 'award',
                'title': 'Achievement Unlocked',
                'description': 'Club reached 100 members milestone',
                'timestamp': '3 days ago'
            },
            {
                'id': 4,
                'icon': 'edit',
                'title': 'Club Details Updated',
                'description': 'Club description and image were updated',
                'timestamp': '1 week ago'
            }
        ]

        # Demo data for events if none exist
        events_data = [
            {
                'id': 1,
                'title': 'AI Workshop Series',
                'date': (timezone.now() + timedelta(days=2)).strftime('%B %d, %Y'),
                'location': 'Tech Hub - Room 301',
                'description': 'Introduction to Machine Learning'
            },
            {
                'id': 2,
                'title': 'Industry Expert Talk',
                'date': (timezone.now() + timedelta(days=5)).strftime('%B %d, %Y'),
                'location': 'Main Auditorium',
                'description': 'Future of Cloud Computing'
            }
        ]

        # Add serialized data to context
        context.update({
            'club_json': json.dumps(club_data, cls=DjangoJSONEncoder),
            'members_json': json.dumps(members_data, cls=DjangoJSONEncoder),
            'activities_json': json.dumps(activities_data, cls=DjangoJSONEncoder),
            'events_json': json.dumps(events_data, cls=DjangoJSONEncoder),
            'roles_json': json.dumps(available_roles, cls=DjangoJSONEncoder),
            'user_role': user_role,
            'is_member': is_member
        })

        return context

    def post(self, request, *args, **kwargs):
        club = self.get_object()
        
        # Check if user is GS before allowing updates
        is_gs = ClubMembership.objects.filter(
            user=request.user,
            club=club,
            role__name='gs'
        ).exists()
        
        if not is_gs:
            return JsonResponse({
                'status': 'error',
                'message': 'Permission denied'
            }, status=403)

        if 'description' in request.POST:
            club.description = request.POST['description']
        if 'image' in request.FILES:
            club.image = request.FILES['image']
            
        club.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Club updated successfully'
        })

    def get_success_url(self):
        return reverse_lazy('club_detail', kwargs={'pk': self.object.pk})


class ClubMemberManagementView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        club = get_object_or_404(Club, pk=self.kwargs['pk'])
        return ClubMembership.objects.filter(
            user=self.request.user,
            club=club,
            role__name__in=['gs', 'Joint Secretary']
        ).exists()

    def post(self, request, *args, **kwargs):
        club = get_object_or_404(Club, pk=self.kwargs['pk'])
        member_id = request.POST.get('member_id')
        action = request.POST.get('action')

        if action == 'update_role':
            new_role = request.POST.get('role')
            if new_role == 'gs':
                ClubMembership.objects.filter(
                    club=club, 
                    role__name='gs'
                ).update(role=ClubRole.objects.get(name='Member'))
            
            membership = get_object_or_404(ClubMembership, club=club, user_id=member_id)
            membership.role = get_object_or_404(ClubRole, name=new_role)
            membership.save()

        elif action == 'blacklist':
            membership = get_object_or_404(ClubMembership, club=club, user_id=member_id)
            if membership.blacklisted:
                membership.blacklisted = False
            else:
                membership.blacklisted = True
            membership.save()

        return JsonResponse({'status': 'success'})

class LeaveClubView(LoginRequiredMixin, View):
    def post(self, request, pk):
        club = get_object_or_404(Club, pk=pk)
        membership = get_object_or_404(ClubMembership, 
            user=request.user,
            club=club
        )
        
        # Don't allow GS to leave without appointing new GS
        if membership.role and membership.role.name == 'gs':
            return JsonResponse({
                'status': 'error',
                'message': 'General Secretary must appoint a replacement before leaving'
            }, status=400)
            
        membership.delete()
        return JsonResponse({'status': 'success'})

class AddClubMemberView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        club = get_object_or_404(Club, pk=self.kwargs['pk'])
        return ClubMembership.objects.filter(
            user=self.request.user,
            club=club,
            role__name__in=['gs', 'Joint Secretary']
        ).exists()
        
    def post(self, request, pk):
        data = json.loads(request.body)
        club = get_object_or_404(Club, pk=pk)
        user_id = data.get('user_id')
        
        membership = ClubMembership.objects.create(
            club=club,
            user_id=user_id,
            role=ClubRole.objects.get(name='Member')
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Member added successfully'
        })