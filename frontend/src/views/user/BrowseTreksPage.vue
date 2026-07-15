<script setup>
import { ref, onMounted } from 'vue'
import AppNav from '@/components/AppNav.vue'
import UserNav from '@/components/user/UserNav.vue'
import { apiFetch } from '@/lib/api'

const treks = ref([])
const search = ref('')
const loading = ref(true)
const error = ref('')
const bookingId = ref(null)
const message = ref('')

async function loadTreks() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({ status: 'open' })
    if (search.value) params.set('q', search.value)
    const data = await apiFetch(`/api/treks?${params.toString()}`)
    treks.value = data.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function bookTrek(trek) {
  bookingId.value = trek.id
  message.value = ''
  error.value = ''
  try {
    await apiFetch('/api/users/bookings', {
      method: 'POST',
      body: JSON.stringify({ trek_id: trek.id, payment_status: 'pending' }),
    })
    message.value = `Booked "${trek.name}" — payment is pending.`
    await loadTreks()
  } catch (err) {
    error.value = err.message
  } finally {
    bookingId.value = null
  }
}

onMounted(loadTreks)
</script>

<template>
  <AppNav />
  <div class="container my-4">
    <UserNav />
    <h1 class="h4 mb-3">Browse Treks</h1>

    <div class="d-flex gap-2 mb-3">
      <input
        v-model="search"
        type="text"
        class="form-control"
        style="max-width: 300px"
        placeholder="Search by name or location…"
        @keyup.enter="loadTreks"
      />
      <button type="button" class="btn btn-outline-secondary" @click="loadTreks">Search</button>
    </div>

    <div v-if="message" class="alert alert-success py-2 small">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading treks…</p>

    <div v-else-if="treks.length" class="row row-cols-1 row-cols-md-3 g-3">
      <div v-for="trek in treks" :key="trek.id" class="col">
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <h3 class="h6">{{ trek.name }}</h3>
            <p class="text-muted small mb-1">{{ trek.location }} · {{ trek.difficulty }} · {{ trek.duration_days }} days</p>
            <p class="text-muted small mb-2">Starts {{ trek.start_date }} · {{ trek.available_slots }} slots left</p>
            <button
              type="button"
              class="btn btn-primary mt-auto"
              :disabled="bookingId === trek.id || trek.available_slots <= 0"
              @click="bookTrek(trek)"
            >
              {{ trek.available_slots <= 0 ? 'Full' : bookingId === trek.id ? 'Booking…' : 'Book Now' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <p v-else class="text-muted">No open treks match your search.</p>
  </div>
</template>
