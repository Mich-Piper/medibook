# backend/appointments/serializers.py
from rest_framework import serializers
from .models import Appointment, TimeSlot, Doctor, Clinic


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Clinic
        fields = ['id', 'name', 'address', 'phone']


class DoctorSerializer(serializers.ModelSerializer):
    display_name   = serializers.CharField(source='user.get_full_name', read_only=True)
    clinic         = ClinicSerializer(read_only=True)

    class Meta:
        model  = Doctor
        fields = ['id', 'display_name', 'specialisation', 'bio', 'avatar_url', 'clinic']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TimeSlot
        fields = ['id', 'date', 'start_time', 'end_time', 'is_available']


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    slot_date   = serializers.DateField(source='time_slot.date',       read_only=True)
    slot_time   = serializers.TimeField(source='time_slot.start_time', read_only=True)

    class Meta:
        model  = Appointment
        fields = ['id', 'doctor', 'doctor_name', 'time_slot', 'slot_date',
                  'slot_time', 'status', 'reason', 'notes', 'created_at']
        read_only_fields = ['status', 'notes', 'created_at']
