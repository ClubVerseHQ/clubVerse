from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Index
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.universities.models import University, Department

# Role Model - Single Responsibility Principle, Optimized for Querying
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        indexes = [
            Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

def get_default_role():
    return Role.objects.filter(name="STUDENT").first()

# User Model - Open/Closed Principle, Liskov Substitution Principle, Optimized for Querying
class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,blank=True,default=get_default_role)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set', 
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='custom_user_permissions_set', 
        blank=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        indexes = [
            Index(fields=['email']),
            Index(fields=['role']),
            Index(fields=['university']),
            Index(fields=['department']),
        ]

    def clean(self):
        if self.email:
            email_prefix = self.email.split('@')[0]  # Get the email prefix before '@'
            
            # Extract department code (1 or 2 characters from the start of the email prefix)
            department_code = email_prefix[:2] if len(email_prefix) > 1 and not email_prefix[1].isdigit() else email_prefix[0]

            # Check if the department code exists in the Department model
            department = Department.objects.filter(code=department_code).first()
            if department:
                self.department = department
            else:
                self.department = None

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation before saving
        if not self.username:
            self.username = self.email
        if not self.profile_picture:
            self.profile_picture = f"https://ui-avatars.com/api/?name={self.first_name}+{self.last_name}&background=random"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.email


# OTP Model - Single Responsibility Principle, Optimized for Querying
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    otp_secret = models.CharField(max_length=100)  # Store base32 secret
    created_at = models.DateTimeField(auto_now_add=True)
    attempt_count = models.PositiveSmallIntegerField(default=1)  # Number of attempts made
    last_attempt = models.DateTimeField(auto_now=True)  # Timestamp of last attempt
    purpose = models.CharField(max_length=20, choices=[
        ('VERIFY', 'Email Verification'),
        ('RESET', 'Password Reset'),
        ('SECONDARY', 'Add Secondary Email')
    ])

    class Meta:
        indexes = [
            Index(fields=['user', 'purpose']),
            Index(fields=['created_at']),
        ]

    def increment_attempt(self):
        """
        Increment the OTP attempt count and update the last attempt timestamp.
        """
        self.attempt_count += 1
        self.last_attempt = timezone.now()
        self.save()

    @classmethod
    def cleanup_expired_otps(cls):
        """
        Clean up OTPs that are older than 2 hours.
        """
        expiry_time = timezone.now() - timedelta(hours=2)
        cls.objects.filter(created_at__lt=expiry_time).delete()