# MediBook — Clinic Appointment Booking System

Patient appointment scheduling web app for a private clinic chain. Doctor calendars, SMS reminders via Termii, patient records, and a Django admin panel for clinic staff.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Django 4.2, Django REST Framework |
| Frontend | Vue.js 3 (Composition API), Pinia, TailwindCSS |
| Database | PostgreSQL |
| SMS | Termii API |
| Task Queue | Celery + Redis (daily reminders) |
| Auth | JWT (djangorestframework-simplejwt) |
| Deploy | Render (API + worker) |

## Project Structure

```
medibook/
├── backend/
│   ├── medibook/
│   │   └── settings.py           # Django settings (JWT, Celery, Termii config)
│   ├── accounts/                 # Custom User model + JWT views
│   ├── appointments/
│   │   ├── models.py             # Doctor, Clinic, TimeSlot, Appointment
│   │   ├── views.py              # DRF ViewSets with race-condition safe booking
│   │   └── tasks.py              # Celery: daily reminder SMS at 08:00
│   ├── patients/                 # PatientProfile + MedicalRecord models
│   ├── notifications/
│   │   └── termii.py             # Termii SMS client with Nigerian number normalisation
│   └── requirements.txt
└── frontend/src/
    └── views/
        └── BookAppointment.vue   # 3-step booking flow (doctor → slot → confirm)
```

## Quick Start

```bash
git clone https://github.com/michelllepiper/medibook.git
cd medibook/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DB, TERMII_API_KEY, etc.
python manage.py migrate && python manage.py createsuperuser
python manage.py runserver    # API on :8000

# Celery worker (new terminal)
celery -A medibook worker -l info
celery -A medibook beat -l info   # scheduler for daily reminders

# Frontend (new terminal)
cd ../frontend && npm install && npm run dev
```

## Booking Flow

1. Patient selects a doctor and date
2. Available `TimeSlot` records are fetched in real time
3. On confirm, slot is locked via `SELECT FOR UPDATE` (prevents double-booking)
4. SMS confirmation sent via Termii immediately
5. Celery beat sends reminder SMS at 08:00 the day before the appointment

---
Built by [Michelle Piper](https://github.com/michelllepiper)
