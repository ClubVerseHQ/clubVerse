from django.contrib import admin
from apps.users.models import OTP, University, Role, User, Department

admin.site.register(University)
admin.site.register(Department)
admin.site.register(OTP)
admin.site.register(Role)
admin.site.register(User)
# Register your models here.
