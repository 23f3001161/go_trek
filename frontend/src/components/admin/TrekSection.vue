<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'


const FILTER_STATUSES = ['pending', 'approved', 'open', 'closed', 'completed']

const ALL_STATUSES = ['pending', 'approved', 'open', 'started', 'closed', 'completed']
const DIFFICULTIES = ['easy', 'moderate', 'hard']

const auth = useAuthStore()

const treks = ref([])
const staffOptions = ref([])
const search = ref('')
const statusFilter = ref('')
const loading = ref(false)
const error = ref('')

const showCreateForm = ref(false)
const createForm = ref({
  name: '',
  location: '',
  difficulty: 'easy',
  duration_days: 1,
  total_slots: 10,
  start_date: '',
  end_date: '',
})
const creating = ref(false)
const createError = ref('')

async function loadTreks() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('q', search.value)
    if (statusFilter.value) params.set('status', statusFilter.value)
    const data = await apiFetch(`/api/treks?${params.toString()}`)
    treks.value = data.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function loadStaffOptions() {
  try {
    const data = await apiFetch('/api/staffs')
    staffOptions.value = data.data
  } catch {

  }
}

async function createTrek() {
  creating.value = true
  createError.value = ''
  try {
   
    await apiFetch('/api/treks', {
      method: 'POST',
      body: JSON.stringify({ ...createForm.value, created_by: auth.id }),
    })
    createForm.value = {
      name: '',
      location: '',
      difficulty: 'easy',
      duration_days: 1,
      total_slots: 10,
      start_date: '',
      end_date: '',
    }
    showCreateForm.value = false
    await loadTreks()
  } catch (err) {
    createError.value = err.message
  } finally {
    creating.value = false
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

async function assignStaff(trek, staffId) {
  try {
    await apiFetch(`/api/treks/${trek.id}`, {
      method: 'PUT',
      body: JSON.stringify({ assigned_staff_id: staffId ? Number(staffId) : null }),
    })
    const match = staffOptions.value.find((s) => s.id === Number(staffId))
    trek.staff_assigned = match ? match.name : null
  } catch (err) {
    error.value = err.message
  }
}

async function cancelTrek(trek) {
  try {
    await apiFetch(`/api/treks/${trek.id}`, { method: 'DELETE' })
    trek.status = 'closed'
  } catch (err) {
    error.value = err.message
  }
}

onMounted(() => {
  loadTreks()
  loadStaffOptions()
})
</script>

<template>
  <div>
    <div class="d-flex gap-2 mb-3 flex-wrap">
      <input
        v-model="search"
        type="text"
        class="form-control"
        style="max-width: 260px"
        placeholder="Search by name or location…"
        @keyup.enter="loadTreks"
      />
      <select v-model="statusFilter" class="form-select" style="max-width: 180px" @change="loadTreks">
        <option value="">All statuses</option>
        <option v-for="s in FILTER_STATUSES" :key="s" :value="s">{{ s }}</option>
      </select>
      <button type="button" class="btn btn-outline-secondary" @click="loadTreks">Search</button>
      <button type="button" class="btn btn-primary ms-auto" @click="showCreateForm = !showCreateForm">
        {{ showCreateForm ? 'Cancel' : '+ Add Trek' }}
      </button>
    </div>

    <form v-if="showCreateForm" class="card card-body mb-3" @submit.prevent="createTrek">
      <div class="row g-2">
        <div class="col-md-3">
          <input v-model="createForm.name" type="text" class="form-control" placeholder="Trek name" required />
        </div>
        <div class="col-md-3">
          <input v-model="createForm.location" type="text" class="form-control" placeholder="Location" required />
        </div>
        <div class="col-md-2">
          <select v-model="createForm.difficulty" class="form-select">
            <option v-for="d in DIFFICULTIES" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <input
            v-model.number="createForm.duration_days"
            type="number"
            min="1"
            class="form-control"
            placeholder="Duration (days)"
            required
          />
        </div>
        <div class="col-md-2">
          <input
            v-model.number="createForm.total_slots"
            type="number"
            min="1"
            class="form-control"
            placeholder="Total slots"
            required
          />
        </div>
        <div class="col-md-3">
          <input v-model="createForm.start_date" type="date" class="form-control" required />
        </div>
        <div class="col-md-3">
          <input v-model="createForm.end_date" type="date" class="form-control" required />
        </div>
      </div>
      <button type="submit" class="btn btn-primary mt-2" :disabled="creating">
        {{ creating ? 'Creating…' : 'Create Trek' }}
      </button>
      <div v-if="createError" class="alert alert-danger py-2 small mt-2 mb-0">{{ createError }}</div>
    </form>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading treks…</p>

    <table v-else-if="treks.length" class="table table-striped align-middle">
      <thead>
        <tr>
          <th>Name</th>
          <th>Location</th>
          <th>Difficulty</th>
          <th>Dates</th>
          <th>Slots</th>
          <th>Status</th>
          <th>Staff</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="trek in treks" :key="trek.id">
          <td>{{ trek.name }}</td>
          <td>{{ trek.location }}</td>
          <td>{{ trek.difficulty }}</td>
          <td>{{ trek.start_date }} · {{ trek.duration_days }}d</td>
          <td>{{ trek.available_slots }}</td>
          <td>
            <select
              class="form-select form-select-sm"
              :value="trek.status"
              @change="updateStatus(trek, $event.target.value)"
            >
              <option v-for="s in ALL_STATUSES" :key="s" :value="s">{{ s }}</option>
            </select>
          </td>
          <td>
            <select
              class="form-select form-select-sm"
              :value="staffOptions.find((s) => s.name === trek.staff_assigned)?.id || ''"
              @change="assignStaff(trek, $event.target.value)"
            >
              <option value="">Unassigned</option>
              <option v-for="s in staffOptions" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </td>
          <td>
            <button type="button" class="btn btn-sm btn-outline-danger" @click="cancelTrek(trek)">Cancel</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-muted">No treks found.</p>
  </div>
</template>
