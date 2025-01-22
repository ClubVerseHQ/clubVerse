from django.db import models
from apps.users.models import User
from apps.universities.models import Department

class ClubType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    type = models.ForeignKey(ClubType, on_delete=models.CASCADE, related_name="clubs")
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="clubs"
    )
    image = models.ImageField(upload_to='club_images/',default='club_images/default.png')
    members = models.ManyToManyField(User, through="ClubMembership", related_name="clubs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)
    deletion_date = models.DateTimeField(null=True, blank=True, db_index=True)

    def __str__(self):
        return f"{self.name} ({self.type.name})"

    @property
    def member_count(self):
        return self.members.count()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Club"
        verbose_name_plural = "Clubs"


class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class ClubRole(models.Model):
    name = models.CharField(max_length=50, unique=True)
    default_permissions = models.ManyToManyField(
        Permission, through="RolePermission", related_name="roles"
    )

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(ClubRole, on_delete=models.CASCADE, related_name="permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("role", "permission")
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class ClubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey(ClubRole, on_delete=models.SET_NULL, null=True, blank=True)
    blacklisted = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "club")
        ordering = ["-joined_at"]
        verbose_name = "Club Membership"
        verbose_name_plural = "Club Memberships"

    def __str__(self):
        role_display = f" ({self.role.name})" if self.role else ""
        return f"{self.user.username} in {self.club.name}{role_display}"

    @property
    def is_active_member(self):
        return not self.blacklisted
