<script setup>
import { ref, onMounted } from 'vue'
import AppNav from '@/components/AppNav.vue'
import UserNav from '@/components/user/UserNav.vue'
import { apiFetch } from '@/lib/api'

const bookings = ref([])
const loading = ref(true)
const error = ref('')
const csvStatus = ref('')

async function loadBookings() {
  loading.value = true
  error.value = ''
  try {
    const data = await apiFetch('/api/users/bookings')

    bookings.value = Array.isArray(data) ? data : data.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function cancelBooking(booking) {
  if (!confirm(`Cancel your booking for "${booking.trek.name}"?`)) return
  try {
    await apiFetch('/api/users/bookings', {
      method: 'DELETE',
      body: JSON.stringify({ id: booking.booking_id }),
    })
    booking.status = 'cancelled'
  } catch (err) {
    error.value = err.message
  }
}


async function exportCsv() {
  csvStatus.value = 'Starting export…'
  try {
    const data = await apiFetch('/api/csv')
    pollCsvStatus(data.task_id, 0)
  } catch (err) {
    csvStatus.value = err.message
  }
}

async function pollCsvStatus(taskId, attempt) {
  if (attempt > 15) {
    csvStatus.value = 'Still processing — check your email shortly.'
    return
  }
  try {
    const data = await apiFetch(`/api/users/status/${taskId}`)
    if (data.status === 'SUCCESS') {
      csvStatus.value = 'Export complete — check your email.'
    } else if (data.status === 'FAILURE') {
      csvStatus.value = 'Export failed. Please try again.'
    } else {
      setTimeout(() => pollCsvStatus(taskId, attempt + 1), 2000)
    }
  } catch (err) {
    csvStatus.value = err.message
  }
}

onMounted(loadBookings)
</script>

<template>
  <AppNav />
  <div class="container my-4">
    <UserNav />
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h1 class="h4 mb-0">My Bookings</h1>
      <button type="button" class="btn btn-outline-secondary btn-sm" @click="exportCsv">Export CSV</button>
    </div>
    <div v-if="csvStatus" class="alert alert-success py-2 small">{{ csvStatus }}</div>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading bookings…</p>

    <table v-else-if="bookings.length" class="table table-striped align-middle">
      <thead>
        <tr>
          <th>Trek</th>
          <th>Dates</th>
          <th>Status</th>
          <th>Payment</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in bookings" :key="b.booking_id">
          <td>{{ b.trek.name }}</td>
          <td>{{ b.trek.start_date }}</td>
          <td><span class="badge bg-secondary">{{ b.status }}</span></td>
          <td>{{ b.payment_status }}</td>
          <td class="text-nowrap">
            <RouterLink :to="`/user/bookings/${b.booking_id}`" class="btn btn-sm btn-outline-secondary me-1">
              Details
            </RouterLink>
            <button
              v-if="b.status !== 'cancelled'"
              type="button"
              class="btn btn-sm btn-outline-danger"
              @click="cancelBooking(b)"
            >
              Cancel
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-muted">You haven't booked any treks yet.</p>
  </div>
</template>
