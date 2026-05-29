# backend/appointments/views.py
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Appointment, TimeSlot, Doctor
from .serializers import AppointmentSerializer, TimeSlotSerializer, DoctorSerializer
from notifications.termii import send_sms
import datetime


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.select_related('user', 'clinic').all()
    serializer_class = DoctorSerializer

    @action(detail=True, methods=['get'], url_path='availability')
    def availability(self, request, pk=None):
        """Return available time slots for a doctor on a given date."""
        doctor = self.get_object()
        date_str = request.query_params.get('date')

        if not date_str:
            return Response({'error': 'date param required (YYYY-MM-DD)'}, status=400)

        try:
            date = datetime.date.fromisoformat(date_str)
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)

        if date < timezone.now().date():
            return Response({'error': 'Cannot book in the past'}, status=400)

        slots = TimeSlot.objects.filter(
            doctor=doctor, date=date, is_available=True
        ).order_by('start_time')

        return Response(TimeSlotSerializer(slots, many=True).data)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Appointment.objects.filter(
                patient__user=user
            ).select_related('doctor__user', 'time_slot').order_by('-time_slot__date')
        elif user.role in ('doctor',):
            return Appointment.objects.filter(
                doctor__user=user
            ).select_related('patient__user', 'time_slot').order_by('time_slot__date')
        # Receptionist / Admin — see all in their clinic
        return Appointment.objects.select_related(
            'doctor__user', 'patient__user', 'time_slot'
        ).all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        slot_id = serializer.validated_data['time_slot'].id

        # Double-check availability inside a select_for_update to prevent race conditions
        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            slot = TimeSlot.objects.select_for_update().get(pk=slot_id)
            if not slot.is_available:
                return Response({'error': 'This slot has just been taken'}, status=409)
            appt = serializer.save()

        # Send SMS confirmation
        try:
            phone = appt.patient.phone_number
            send_sms(
                phone,
                f"Confirmed: Appointment with Dr. {appt.doctor.user.last_name} "
                f"on {appt.time_slot.date} at {appt.time_slot.start_time}. "
                f"Reply CANCEL to cancel. — MediBook"
            )
        except Exception as e:
            # Non-fatal — log and continue
            print(f"[SMS] Failed to send confirmation: {e}")

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appt = self.get_object()
        if appt.status not in ('pending', 'confirmed'):
            return Response({'error': 'Cannot cancel a completed appointment'}, status=400)
        appt.status = 'cancelled'
        appt.save()
        send_sms(
            appt.patient.phone_number,
            f"Your appointment with Dr. {appt.doctor.user.last_name} on "
            f"{appt.time_slot.date} has been cancelled. — MediBook"
        )
        return Response({'status': 'cancelled'})
