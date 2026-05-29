# backend/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('patient',      'Patient'),
        ('doctor',       'Doctor'),
        ('receptionist', 'Receptionist'),
        ('admin',        'Admin'),
    ]
    role  = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
