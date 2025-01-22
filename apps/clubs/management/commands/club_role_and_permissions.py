from django.core.management.base import BaseCommand
from apps.clubs.models import ClubRole, Permission

class Command(BaseCommand):
    help = 'Set up initial ClubRole and Permission instances'

    def handle(self, *args, **options):
        # Create Permissions
        permissions = [
            ('edit_club_info', 'Can edit club information'),
            ('add_member', 'Can add new members'),
            ('remove_member', 'Can remove members'),
            ('blacklist_member', 'Can blacklist members'),
            ('create_event', 'Can create events'),
            ('update_event', 'Can update events'),
            ('delete_event', 'Can delete events'),
        ]

        for name, description in permissions:
            Permission.objects.get_or_create(name=name, defaults={'description': description})

        # Create ClubRoles
        gs_role, _ = ClubRole.objects.get_or_create(name='General Secretary')
        member_role, _ = ClubRole.objects.get_or_create(name='Member')

        # Assign permissions to roles
        all_permissions = Permission.objects.all()
        gs_role.default_permissions.set(all_permissions)
        # Members have no default permissions

        self.stdout.write(self.style.SUCCESS('Successfully set up club roles and permissions'))

