# backend/appointments/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, AppointmentViewSet

router = DefaultRouter()
router.register('doctors',      DoctorViewSet,      basename='doctor')
router.register('',             AppointmentViewSet, basename='appointment')

urlpatterns = [path('', include(router.urls))]
