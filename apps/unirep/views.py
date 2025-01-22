from django.views.generic import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from apps.clubs.models import Club, ClubMembership, ClubRole
from apps.users.models import User
from django.shortcuts import get_object_or_404

class UnirepRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role and self.request.user.role.name == 'UNIREP'

class ClubCreateView(UnirepRequiredMixin, CreateView):
    model = Club
    fields = ['name', 'description', 'type', 'department', 'image_url']
    template_name = 'unirep/create_club.html'
    success_url = reverse_lazy('club_list')

class ClubDeleteView(UnirepRequiredMixin, DeleteView):
    model = Club
    template_name = 'unirep/delete_club.html'
    success_url = reverse_lazy('club_list')

class ClubChangeDetailsView(UnirepRequiredMixin, UpdateView):
    model = Club
    fields = ['name', 'description', 'type', 'department', 'image_url']
    template_name = 'unirep/change_club_details.html'

    def get_success_url(self):
        return reverse_lazy('club_detail', kwargs={'pk': self.object.pk})

class AppointGSView(UnirepRequiredMixin, UpdateView):
    model = Club
    template_name = 'unirep/appoint_gs.html'
    fields = []  # We don't need any fields from the Club model

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.members.all()
        return context

    def post(self, request, *args, **kwargs):
        club = self.get_object()
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        gs_role = ClubRole.objects.get(name='General Secretary')
        ClubMembership.objects.update_or_create(
            user=user,
            club=club,
            defaults={'role': gs_role}
        )
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('club_detail', kwargs={'pk': self.object.pk})

