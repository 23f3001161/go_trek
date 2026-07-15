<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/lib/api'
const BOOKING_STATUSES = ['booked', 'cancelled', 'completed', 'waitlist']

const bookings = ref([])
const search = ref('')
const statusFilter = ref('')
const loading = ref(false)
const error = ref('')

async function loadBookings() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('q', search.value)
    if (statusFilter.value) params.set('status', statusFilter.value)
    const data = await apiFetch(`/api/bookings?${params.toString()}`)
    bookings.value = data.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadBookings)
</script>

<template>
  <div>
    <div class="d-flex gap-2 mb-3 flex-wrap">
      <input
        v-model="search"
        type="text"
        class="form-control"
        style="max-width: 260px"
        placeholder="Search by user or trek name…"
        @keyup.enter="loadBookings"
      />
      <select v-model="statusFilter" class="form-select" style="max-width: 180px" @change="loadBookings">
        <option value="">All statuses</option>
        <option v-for="s in BOOKING_STATUSES" :key="s" :value="s">{{ s }}</option>
      </select>
      <button type="button" class="btn btn-outline-secondary" @click="loadBookings">Search</button>
    </div>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading bookings…</p>

    <table v-else-if="bookings.length" class="table table-striped align-middle">
      <thead>
        <tr>
          <th>User</th>
          <th>Trek</th>
          <th>Status</th>
          <th>Payment</th>
          <th>Booked on</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="booking in bookings" :key="booking.booking_id">
          <td>{{ booking.user_name }}</td>
          <td>{{ booking.trek_name }}</td>
          <td><span class="badge bg-secondary">{{ booking.status }}</span></td>
          <td><span class="badge bg-secondary">{{ booking.payment_status }}</span></td>
          <td>{{ new Date(booking.booking_date).toLocaleDateString() }}</td>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-muted">No bookings found.</p>
  </div>
</template>
