<script setup>
import { ref, onMounted } from 'vue'
import AppNav from '@/components/AppNav.vue'
import UserNav from '@/components/user/UserNav.vue'
import { apiFetch } from '@/lib/api'

const history = ref([])
const loading = ref(true)
const error = ref('')

async function loadHistory() {
  loading.value = true
  error.value = ''
  try {
    const data = await apiFetch('/api/users/history')
    history.value = data.booked_treks
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadHistory)
</script>

<template>
  <AppNav />
  <div class="container my-4">
    <UserNav />
    <h1 class="h4 mb-3">Trek History</h1>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading history…</p>

    <table v-else-if="history.length" class="table table-striped align-middle">
      <thead>
        <tr>
          <th>Trek</th>
          <th>Location</th>
          <th>Dates</th>
          <th>Status</th>
          <th>Payment</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="h in history" :key="h.booking_id">
          <td>{{ h.trek_name }}</td>
          <td>{{ h.location }}</td>
          <td>{{ h.start_date }} &rarr; {{ h.end_date }}</td>
          <td><span class="badge bg-secondary">{{ h.booking_status }}</span></td>
          <td>{{ h.payment_status }}</td>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-muted">No trek history yet — non-cancelled bookings will show up here.</p>
  </div>
</template>
