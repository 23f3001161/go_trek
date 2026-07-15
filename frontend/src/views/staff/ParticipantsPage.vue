<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppNav from '@/components/AppNav.vue'
import { apiFetch } from '@/lib/api'


const BOOKING_STATUSES = ['booked', 'cancelled', 'completed']

const route = useRoute()
const trekId = route.params.id

const trekName = ref('')
const participants = ref([])
const loading = ref(true)
const error = ref('')

async function loadParticipants() {
  loading.value = true
  error.value = ''
  try {
    const data = await apiFetch(`/api/staff/treks/${trekId}/participants`)
    trekName.value = data.trek_name
    participants.value = data.participants
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function updateBookingStatus(participant, status) {
  try {
    await apiFetch(`/api/bookings/${participant.booking_id}`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    })
    participant.booking_status = status
  } catch (err) {
    error.value = err.message
  }
}

onMounted(loadParticipants)
</script>

<template>
  <AppNav />
  <div class="container my-4">
    <RouterLink to="/staff" class="d-inline-block mb-3 small">&larr; Back to assigned treks</RouterLink>
    <h1 class="h4 mb-3">Participants{{ trekName ? ` — ${trekName}` : '' }}</h1>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading participants…</p>

    <table v-else-if="participants.length" class="table table-striped align-middle">
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Payment</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in participants" :key="p.booking_id">
          <td>{{ p.name }}</td>
          <td>{{ p.email }}</td>
          <td>{{ p.phone }}</td>
          <td>{{ p.payment_status }}</td>
          <td>
            <select
              class="form-select form-select-sm"
              :value="p.booking_status"
              @change="updateBookingStatus(p, $event.target.value)"
            >
              <option v-for="s in BOOKING_STATUSES" :key="s" :value="s">{{ s }}</option>
            </select>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-muted">No one has booked this trek yet.</p>
  </div>
</template>
