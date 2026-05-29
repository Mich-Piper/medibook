<!-- frontend/src/views/BookAppointment.vue -->
<template>
  <div class="book-appointment">
    <h2>Book an Appointment</h2>

    <!-- Step 1: Select doctor -->
    <section v-if="step === 'doctor'">
      <h3>Choose a Doctor</h3>
      <div class="doctor-grid">
        <div
          v-for="doctor in doctors"
          :key="doctor.id"
          class="doctor-card"
          :class="{ selected: selectedDoctor?.id === doctor.id }"
          @click="selectDoctor(doctor)"
        >
          <img :src="doctor.avatar_url || '/default-avatar.png'" :alt="doctor.user.display_name" />
          <div>
            <strong>Dr. {{ doctor.user.last_name }}</strong>
            <span>{{ doctor.specialisation }}</span>
            <span class="clinic">{{ doctor.clinic.name }}</span>
          </div>
        </div>
      </div>
      <button class="btn-primary" :disabled="!selectedDoctor" @click="step = 'slot'">
        Continue
      </button>
    </section>

    <!-- Step 2: Pick a slot -->
    <section v-if="step === 'slot'">
      <h3>Pick a Date &amp; Time — Dr. {{ selectedDoctor?.user.last_name }}</h3>
      <input type="date" v-model="selectedDate" :min="minDate" @change="loadSlots" />

      <div v-if="loadingSlots" class="loading">Loading slots…</div>

      <div v-else-if="slots.length === 0 && selectedDate" class="no-slots">
        No available slots on this date.
      </div>

      <div v-else class="slot-grid">
        <button
          v-for="slot in slots"
          :key="slot.id"
          class="slot-btn"
          :class="{ selected: selectedSlot?.id === slot.id }"
          @click="selectedSlot = slot"
        >
          {{ formatTime(slot.start_time) }}
        </button>
      </div>

      <div class="actions">
        <button class="btn-secondary" @click="step = 'doctor'">Back</button>
        <button class="btn-primary" :disabled="!selectedSlot" @click="step = 'confirm'">
          Continue
        </button>
      </div>
    </section>

    <!-- Step 3: Confirm -->
    <section v-if="step === 'confirm'">
      <h3>Confirm Appointment</h3>
      <div class="summary-card">
        <p><strong>Doctor:</strong> Dr. {{ selectedDoctor?.user.last_name }}</p>
        <p><strong>Specialisation:</strong> {{ selectedDoctor?.specialisation }}</p>
        <p><strong>Date:</strong> {{ selectedDate }}</p>
        <p><strong>Time:</strong> {{ formatTime(selectedSlot?.start_time) }}</p>
      </div>
      <textarea v-model="reason" placeholder="Reason for visit (optional)" rows="3" />
      <div class="actions">
        <button class="btn-secondary" @click="step = 'slot'">Back</button>
        <button class="btn-primary" :disabled="booking" @click="confirmBooking">
          {{ booking ? 'Booking…' : 'Confirm &amp; Book' }}
        </button>
      </div>
    </section>

    <!-- Success -->
    <section v-if="step === 'success'" class="success">
      <div class="success-icon">✅</div>
      <h3>Appointment Confirmed!</h3>
      <p>You'll receive an SMS reminder the day before.</p>
      <router-link to="/appointments" class="btn-primary">View My Appointments</router-link>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAppointmentsStore } from '@/stores/appointments';

const store = useAppointmentsStore();

const step           = ref<'doctor'|'slot'|'confirm'|'success'>('doctor');
const doctors        = ref<any[]>([]);
const selectedDoctor = ref<any>(null);
const selectedDate   = ref('');
const slots          = ref<any[]>([]);
const selectedSlot   = ref<any>(null);
const reason         = ref('');
const loadingSlots   = ref(false);
const booking        = ref(false);

const minDate = computed(() => new Date().toISOString().split('T')[0]);

onMounted(async () => {
  doctors.value = await store.fetchDoctors();
});

function selectDoctor(doctor: any) {
  selectedDoctor.value = doctor;
  selectedSlot.value   = null;
  selectedDate.value   = '';
  slots.value          = [];
}

async function loadSlots() {
  if (!selectedDoctor.value || !selectedDate.value) return;
  loadingSlots.value = true;
  slots.value = await store.fetchSlots(selectedDoctor.value.id, selectedDate.value);
  loadingSlots.value = false;
}

async function confirmBooking() {
  booking.value = true;
  try {
    await store.createAppointment({
      time_slot: selectedSlot.value.id,
      reason:    reason.value,
    });
    step.value = 'success';
  } finally {
    booking.value = false;
  }
}

function formatTime(t?: string) {
  if (!t) return '';
  const [h, m] = t.split(':');
  const hour = parseInt(h);
  return `${hour > 12 ? hour - 12 : hour}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;
}
</script>
