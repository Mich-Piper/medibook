# backend/patients/models.py
from django.db import models
from django.conf import settings


class PatientProfile(models.Model):
    user         = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group  = models.CharField(max_length=5, blank=True)
    allergies    = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} (Patient)"


class MedicalRecord(models.Model):
    patient    = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='records')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis  = models.TextField()
    prescription = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Record for {self.patient} — {self.created_at.date()}"
