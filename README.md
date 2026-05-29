# MediBook — Clinic Appointment Booking System

A patient appointment scheduling web app for a private clinic chain. Features doctor availability calendars, SMS reminders via Termii, patient records management, and a Django admin panel for clinic staff.

## Features

- **Doctor calendars** — availability slots with real-time booking conflict prevention
- **SMS reminders** — automated appointment confirmations and 24h reminders via Termii
- **Patient records** — secure medical history, visit notes, and document uploads
- **Multi-clinic support** — staff log in to their specific clinic; admins see all branches
- **Django admin** — customised admin panel for receptionists to manage bookings
- **Role-based access** — Patient / Receptionist / Doctor / Admin roles
- **Cancellation & rescheduling** — with automated SMS notification on status change

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Django 4.2, Django REST Framework |
| Frontend | Vue.js 3 (Composition API), Pinia, TailwindCSS |
| Database | PostgreSQL |
| SMS | Termii API |
| Task Queue | Celery + Redis (scheduled reminders) |
| Auth | JWT (djangorestframework-simplejwt) |
| Deployment | Render (API + worker), Neon (Postgres) |

## Project Structure

```
medibook/
├── backend/                         # Django project
│   ├── medibook/                    # Django settings, URLs, WSGI
│   ├── accounts/                    # Custom User model + JWT auth views
│   │   ├── models.py                # User with role field
│   │   └── views.py                 # Login, register, profile
│   ├── appointments/
│   │   ├── models.py                # Appointment, TimeSlot, Doctor
│   │   ├── views.py                 # BookingViewSet (DRF)
│   │   ├── serializers.py
│   │   ├── admin.py                 # Customised admin interface
│   │   └── tasks.py                 # Celery tasks: send_reminder_sms
│   ├── patients/
│   │   ├── models.py                # PatientProfile, MedicalRecord
│   │   └── views.py
│   └── notifications/
│       └── termii.py                # Termii SMS client wrapper
├── frontend/                        # Vue.js 3 SPA
│   ├── src/
│   │   ├── views/
│   │   │   ├── BookAppointment.vue
│   │   │   ├── MyAppointments.vue
│   │   │   └── AdminDashboard.vue
│   │   ├── stores/
│   │   │   ├── appointments.ts      # Pinia store
│   │   │   └── auth.ts
│   │   └── components/
│   │       ├── DoctorCard.vue
│   │       ├── TimeSlotPicker.vue
│   │       └── AppointmentCard.vue
└── docker-compose.yml
```

## Getting Started

```bash
git clone https://github.com/michelllepiper/medibook.git
cd medibook

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver     # API on :8000

# In a new terminal — Celery worker for SMS tasks
celery -A medibook worker -l info

# Frontend (another terminal)
cd ../frontend
npm install
npm run dev                    # UI on :5173
```

### Environment Variables

```env
SECRET_KEY=django-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost:5432/medibook
REDIS_URL=redis://localhost:6379
TERMII_API_KEY=TLxxx...
TERMII_SENDER_ID=MediBook
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Key Code: Termii SMS Notification

```python
# backend/notifications/termii.py
import requests
from django.conf import settings

def send_sms(phone_number: str, message: str) -> dict:
    payload = {
        "to": phone_number,
        "from": settings.TERMII_SENDER_ID,
        "sms": message,
        "type": "plain",
        "api_key": settings.TERMII_API_KEY,
        "channel": "generic",
    }
    response = requests.post(
        "https://api.ng.termii.com/api/sms/send",
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
```

## Key Code: Scheduled Celery Reminder

```python
# backend/appointments/tasks.py
from celery import shared_task
from .models import Appointment
from notifications.termii import send_sms

@shared_task
def send_appointment_reminders():
    """Run daily at 8 AM — sends SMS for appointments tomorrow."""
    from django.utils import timezone
    import datetime

    tomorrow = timezone.now().date() + datetime.timedelta(days=1)
    appointments = Appointment.objects.filter(
        date=tomorrow, status='confirmed'
    ).select_related('patient__user', 'doctor__user')

    for appt in appointments:
        phone = appt.patient.phone_number
        msg = (
            f"Reminder: You have an appointment with Dr. {appt.doctor.user.last_name} "
            f"tomorrow at {appt.time_slot}. "
            f"Reply CANCEL to cancel. — MediBook"
        )
        send_sms(phone, msg)
```

---

Built by [Michelle Piper](https://github.com/michelllepiper)
