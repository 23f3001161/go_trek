<script setup>
import { ref, onMounted } from 'vue'
import AppNav from '@/components/AppNav.vue'
import AdminNav from '@/components/admin/AdminNav.vue'
import { apiFetch } from '@/lib/api'

const loading = ref(true)
const error = ref('')

const trekCount = ref(0)
const openTreks = ref(0)
const pendingTreks = ref(0)
const staffCount = ref(0)
const userCount = ref(0)
const bookingCount = ref(0)
const recentTreks = ref([])
const recentBookings = ref([])

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const [treks, staff, users, bookings] = await Promise.all([
      apiFetch('/api/treks'),
      apiFetch('/api/staffs'),
      apiFetch('/api/users'),
      apiFetch('/api/bookings'),
    ])

    trekCount.value = treks.total_treks ?? treks.data.length
    openTreks.value = treks.data.filter((t) => t.status === 'open').length
    pendingTreks.value = treks.data.filter((t) => t.status === 'pending').length
    recentTreks.value = treks.data.slice(0, 5)

    staffCount.value = staff.data.length
    userCount.value = users.data.filter((u) => !u.roles.includes('staff') && !u.roles.includes('admin')).length

    bookingCount.value = bookings.total_bookings ?? bookings.data.length
    recentBookings.value = bookings.data.slice(0, 5)
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
  <div class="container my-4">
    <AdminNav />
    <h1 class="h4 mb-3">Admin Dashboard</h1>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading…</p>

    <template v-else>
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="card text-center h-100">
            <div class="card-body">
              <div class="fs-4 fw-bold">{{ trekCount }}</div>
              <div class="text-muted small">Total Treks</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card text-center h-100">
            <div class="card-body">
              <div class="fs-4 fw-bold">{{ openTreks }}</div>
              <div class="text-muted small">Open Treks</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card text-center h-100">
            <div class="card-body">
              <div class="fs-4 fw-bold">{{ pendingTreks }}</div>
              <div class="text-muted small">Pending Approval</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card text-center h-100">
            <div class="card-body">
              <div class="fs-4 fw-bold">{{ bookingCount }}</div>
              <div class="text-muted small">Total Bookings</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card text-center h-100">
            <div class="card-body">
              <div class="fs-4 fw-bold">{{ staffCount }}</div>
              <div class="text-muted small">Staff Members</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card text-center h-100">
            <div class="card-body">
              <div class="fs-4 fw-bold">{{ userCount }}</div>
              <div class="text-muted small">Users</div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-12 col-md-6">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h2 class="h6 mb-0">Recent treks</h2>
            <RouterLink to="/admin/treks" class="small">View all</RouterLink>
          </div>
          <p v-if="!recentTreks.length" class="text-muted small">No treks yet.</p>
          <ul v-else class="list-group">
            <li
              v-for="t in recentTreks"
              :key="t.id"
              class="list-group-item d-flex justify-content-between align-items-center"
            >
              {{ t.name }} · {{ t.location }}
              <span class="badge bg-secondary text-capitalize">{{ t.status }}</span>
            </li>
          </ul>
        </div>

        <div class="col-12 col-md-6">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h2 class="h6 mb-0">Recent bookings</h2>
            <RouterLink to="/admin/bookings" class="small">View all</RouterLink>
          </div>
          <p v-if="!recentBookings.length" class="text-muted small">No bookings yet.</p>
          <ul v-else class="list-group">
            <li
              v-for="b in recentBookings"
              :key="b.booking_id"
              class="list-group-item d-flex justify-content-between align-items-center"
            >
              {{ b.user_name }} → {{ b.trek_name }}
              <span class="badge bg-secondary text-capitalize">{{ b.status }}</span>
            </li>
          </ul>
        </div>
      </div>
    </template>
  </div>
</template>