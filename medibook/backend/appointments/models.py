# backend/appointments/models.py
from django.db import models
from django.conf import settings


class Clinic(models.Model):
    name    = models.CharField(max_length=200)
    address = models.TextField()
    phone   = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user           = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clinic         = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='doctors')
    specialisation = models.CharField(max_length=100)
    bio            = models.TextField(blank=True)
    avatar_url     = models.URLField(blank=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} — {self.specialisation}"


class TimeSlot(models.Model):
    """One bookable slot per doctor per day."""
    doctor      = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='time_slots')
    date        = models.DateField()
    start_time  = models.TimeField()
    end_time    = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        ordering        = ['date', 'start_time']

    def __str__(self):
        return f"{self.doctor} | {self.date} {self.start_time}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show',   'No Show'),
    ]

    patient   = models.ForeignKey('patients.PatientProfile', on_delete=models.CASCADE, related_name='appointments')
    doctor    = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='appointment')
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason    = models.TextField(blank=True)
    notes     = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time_slot__date', '-time_slot__start_time']

    def save(self, *args, **kwargs):
        # Lock/unlock the slot based on status
        if self.status in ('pending', 'confirmed'):
            TimeSlot.objects.filter(pk=self.time_slot_id).update(is_available=False)
        elif self.status in ('cancelled', 'no_show'):
            TimeSlot.objects.filter(pk=self.time_slot_id).update(is_available=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} → {self.doctor} on {self.time_slot.date}"
