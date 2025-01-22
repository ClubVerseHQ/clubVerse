from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Index

# University Model - Single Responsibility Principle, Optimized for Querying
class University(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)

    class Meta:
        indexes = [
            Index(fields=['domain']),
        ]

    def __str__(self):
        return self.name
    
# Department Model - Single Responsibility Principle, Optimized for Querying
class Department(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='departments')
    full_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)  # unique code for department
    code = models.CharField(max_length=20, unique=True)  # unique code for student id

    class Meta:
        indexes = [
            Index(fields=['code']),
            Index(fields=['university', 'code']),
        ]

    def __str__(self):
        return self.full_name