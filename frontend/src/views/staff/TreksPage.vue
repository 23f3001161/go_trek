<script setup>
import { ref, onMounted } from 'vue'
import AppNav from '@/components/AppNav.vue'
import { apiFetch } from '@/lib/api'


const STAFF_STATUSES = ['started', 'completed']

const treks = ref([])
const loading = ref(true)
const error = ref('')

async function loadTreks() {
  loading.value = true
  error.value = ''
  try {
    const data = await apiFetch('/api/staff/treks')
    treks.value = data.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function updateStatus(trek, status) {
  try {

    await apiFetch(`/api/treks/${trek.id}`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    })
    trek.status = status
  } catch (err) {
    error.value = err.message
  }
}

onMounted(loadTreks)
</script>

<template>
  <AppNav />
  <div class="container my-4">
    <h1 class="h4 mb-3">Assigned Treks</h1>
    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading treks…</p>

    <table v-else-if="treks.length" class="table table-striped align-middle">
      <thead>
        <tr>
          <th>Name</th>
          <th>Location</th>
          <th>Dates</th>
          <th>Slots</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="trek in treks" :key="trek.id">
          <td>{{ trek.name }}</td>
          <td>{{ trek.location }}</td>
          <td>{{ trek.start_date }} · {{ trek.duration_days }}d</td>
          <td>{{ trek.available_slots }}</td>
          <td>
            <select
              class="form-select form-select-sm"
              :value="trek.status"
              @change="updateStatus(trek, $event.target.value)"
            >
              <option :value="trek.status" disabled hidden>{{ trek.status }}</option>
              <option v-for="s in STAFF_STATUSES" :key="s" :value="s">{{ s }}</option>
            </select>
          </td>
          <td>
            <RouterLink :to="`/staff/treks/${trek.id}`" class="btn btn-sm btn-outline-secondary">
              View participants
            </RouterLink>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-muted">No treks assigned to you yet.</p>
  </div>
</template>
