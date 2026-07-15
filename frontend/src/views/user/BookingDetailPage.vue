<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppNav from '@/components/AppNav.vue'
import UserNav from '@/components/user/UserNav.vue'
import { apiFetch } from '@/lib/api'

const route = useRoute()
const bookingId = route.params.id

const booking = ref(null)
const loading = ref(true)
const error = ref('')

async function loadBooking() {
  loading.value = true
  error.value = ''
  try {
    const data = await apiFetch(`/api/users/bookings/${bookingId}`)
    booking.value = data.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadBooking)
</script>

<template>
  <AppNav />
  <div class="container my-4" style="max-width: 600px">
    <UserNav />
    <RouterLink to="/user/bookings" class="d-inline-block mb-3 small">&larr; Back to my bookings</RouterLink>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading booking…</p>

    <div v-else-if="booking" class="card">
      <div class="card-body">
        <h1 class="h5">{{ booking.trek.name }}</h1>
        <p class="text-muted small mb-3">{{ booking.trek.location }} · {{ booking.trek.difficulty }}</p>

        <table class="table table-borderless table-sm mb-0">
          <tbody>
            <tr>
              <th class="text-muted fw-normal" style="width: 160px">Trek dates</th>
              <td>{{ booking.trek.start_date }} &rarr; {{ booking.trek.end_date }}</td>
            </tr>
            <tr>
              <th class="text-muted fw-normal">Trek status</th>
              <td><span class="badge bg-success">{{ booking.trek.status }}</span></td>
            </tr>
            <tr>
              <th class="text-muted fw-normal">Booking status</th>
              <td><span class="badge bg-success">{{ booking.booking_status }}</span></td>
            </tr>
            <tr>
              <th class="text-muted fw-normal">Payment status</th>
              <td>{{ booking.payment_status }}</td>
            </tr>
            <tr>
              <th class="text-muted fw-normal">Booked on</th>
              <td>{{ new Date(booking.booking_date).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
