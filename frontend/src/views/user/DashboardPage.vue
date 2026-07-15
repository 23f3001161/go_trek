<script setup>
import { ref, onMounted } from 'vue'
import AppNav from '@/components/AppNav.vue'
import UserNav from '@/components/user/UserNav.vue'
import { apiFetch } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const availableTreks = ref([])
const bookedTreks = ref([])
const loading = ref(true)
const error = ref('')

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const data = await apiFetch('/api/users/dashboard')
    availableTreks.value = data.available_treks
    bookedTreks.value = data.booked_treks
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <AppNav />
  <div class="container my-4" style="max-width: 700px">
    <UserNav />
    <h1 class="h4 mb-3">Welcome, {{ auth.name }}</h1>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading…</p>

    <template v-else>
      <section class="mb-4">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h2 class="h6 mb-0">Upcoming bookings</h2>
          <RouterLink to="/user/bookings" class="small">View all</RouterLink>
        </div>
        <p v-if="!bookedTreks.length" class="text-muted small">No upcoming bookings yet.</p>
        <ul v-else class="list-group">
          <li
            v-for="b in bookedTreks"
            :key="b.booking_id"
            class="list-group-item d-flex justify-content-between align-items-center"
          >
            {{ b.trek_name }}
            <span class="badge bg-success">{{ b.booking_status }}</span>
          </li>
        </ul>
      </section>

      <section>
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h2 class="h6 mb-0">Open treks</h2>
          <RouterLink to="/user/treks" class="small">Browse all</RouterLink>
        </div>
        <p v-if="!availableTreks.length" class="text-muted small">No open treks right now.</p>
        <ul v-else class="list-group">
          <li
            v-for="t in availableTreks"
            :key="t.id"
            class="list-group-item d-flex justify-content-between align-items-center"
          >
            {{ t.name }} · {{ t.location }}
            <span class="badge bg-success">{{ t.available_slots }} slots left</span>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>
