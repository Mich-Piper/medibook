// frontend/src/stores/appointments.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api';

export const useAppointmentsStore = defineStore('appointments', () => {
  const appointments = ref<any[]>([]);
  const loading      = ref(false);

  async function fetchDoctors() {
    const { data } = await api.get('/appointments/doctors/');
    return data.results ?? data;
  }

  async function fetchSlots(doctorId: number, date: string) {
    const { data } = await api.get(`/appointments/doctors/${doctorId}/availability/?date=${date}`);
    return data;
  }

  async function fetchMyAppointments() {
    loading.value = true;
    try {
      const { data } = await api.get('/appointments/');
      appointments.value = data.results ?? data;
    } finally {
      loading.value = false;
    }
  }

  async function createAppointment(payload: { time_slot: number; reason?: string }) {
    const { data } = await api.post('/appointments/', payload);
    appointments.value.unshift(data);
    return data;
  }

  async function cancelAppointment(id: number) {
    await api.post(`/appointments/${id}/cancel/`);
    const appt = appointments.value.find(a => a.id === id);
    if (appt) appt.status = 'cancelled';
  }

  return { appointments, loading, fetchDoctors, fetchSlots, fetchMyAppointments, createAppointment, cancelAppointment };
});
