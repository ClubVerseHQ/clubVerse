from django.contrib import admin
from apps.clubs.models import Club, ClubMembership, ClubRole, ClubType, Permission, RolePermission

admin.site.register(Club)
admin.site.register(ClubMembership)
admin.site.register(ClubRole)
admin.site.register(ClubType)
admin.site.register(Permission)
admin.site.register(RolePermission)

# Register your models here.
