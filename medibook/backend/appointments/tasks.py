# backend/appointments/tasks.py
from celery import shared_task
from django.utils import timezone
import datetime
from notifications.termii import send_sms


@shared_task(bind=True, max_retries=3)
def send_appointment_reminders(self):
    """
    Runs daily at 08:00 AM.
    Sends an SMS reminder to every patient with a confirmed appointment tomorrow.
    """
    from appointments.models import Appointment

    tomorrow = timezone.now().date() + datetime.timedelta(days=1)
    appointments = Appointment.objects.filter(
        time_slot__date=tomorrow,
        status='confirmed',
    ).select_related('patient__user', 'doctor__user', 'time_slot')

    sent = 0
    for appt in appointments:
        try:
            phone = appt.patient.phone_number
            msg = (
                f"Reminder: You have an appointment with "
                f"Dr. {appt.doctor.user.last_name} tomorrow "
                f"({appt.time_slot.date}) at {appt.time_slot.start_time.strftime('%I:%M %p')}. "
                f"Reply CANCEL to cancel. — MediBook"
            )
            send_sms(phone, msg)
            sent += 1
        except Exception as exc:
            print(f"[SMS reminder] Failed for appt {appt.id}: {exc}")

    return f"Reminders sent: {sent}/{appointments.count()}"


@shared_task
def send_sms_task(phone_number: str, message: str):
    """Fire-and-forget SMS task for use outside of appointment flow."""
    send_sms(phone_number, message)
