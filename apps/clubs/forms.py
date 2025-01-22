from django import forms
from .models import Club, ClubMembership

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'type', 'department', 'image']

class ClubMembershipForm(forms.ModelForm):
    class Meta:
        model = ClubMembership
        fields = ['user', 'role']

