<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/lib/api'

const staff = ref([])
const search = ref('')
const loading = ref(false)
const error = ref('')

const showCreateForm = ref(false)
const createForm = ref({ full_name: '', email: '', phone_number: '', password: '' })
const creating = ref(false)
const createError = ref('')

const editingId = ref(null)
const editForm = ref({ full_name: '', phone: '' })

async function loadStaff() {
  loading.value = true
  error.value = ''
  try {
    const query = search.value ? `?q=${encodeURIComponent(search.value)}` : ''
    const data = await apiFetch(`/api/staffs${query}`)
    staff.value = data.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function createStaff() {
  creating.value = true
  createError.value = ''
  try {
    await apiFetch('/api/staffs', {
      method: 'POST',
      body: JSON.stringify(createForm.value),
    })
    createForm.value = { full_name: '', email: '', phone_number: '', password: '' }
    showCreateForm.value = false
    await loadStaff()
  } catch (err) {
    createError.value = err.message
  } finally {
    creating.value = false
  }
}

async function toggleActive(member) {
  try {
    await apiFetch(`/api/staffs/${member.id}`, {
      method: 'PUT',
      body: JSON.stringify({ active: !member.active }),
    })
    member.active = !member.active
  } catch (err) {
    error.value = err.message
  }
}

function startEdit(member) {
  editingId.value = member.id
  editForm.value = { full_name: member.name, phone: member.phone_number }
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(member) {
  try {
    await apiFetch(`/api/staffs/${member.id}`, {
      method: 'PUT',
      body: JSON.stringify(editForm.value),
    })
    member.name = editForm.value.full_name
    member.phone_number = editForm.value.phone
    editingId.value = null
  } catch (err) {
    error.value = err.message
  }
}

onMounted(loadStaff)
</script>

<template>
  <div>
    <div class="d-flex gap-2 mb-3">
      <input
        v-model="search"
        type="text"
        class="form-control"
        placeholder="Search by name, email, or phone…"
        @keyup.enter="loadStaff"
      />
      <button type="button" class="btn btn-outline-secondary text-nowrap" @click="loadStaff">Search</button>
      <button type="button" class="btn btn-primary text-nowrap" @click="showCreateForm = !showCreateForm">
        {{ showCreateForm ? 'Cancel' : '+ Add Staff' }}
      </button>
    </div>

    <form v-if="showCreateForm" class="card card-body mb-3" @submit.prevent="createStaff">
      <div class="row g-2">
        <div class="col-md-3">
          <input v-model="createForm.full_name" type="text" class="form-control" placeholder="Full name" required />
        </div>
        <div class="col-md-3">
          <input v-model="createForm.email" type="email" class="form-control" placeholder="Email" required />
        </div>
        <div class="col-md-3">
          <input v-model="createForm.phone_number" type="text" class="form-control" placeholder="Phone number" required />
        </div>
        <div class="col-md-3">
          <input
            v-model="createForm.password"
            type="password"
            class="form-control"
            placeholder="Temporary password"
            required
          />
        </div>
      </div>
      <button type="submit" class="btn btn-primary mt-2" :disabled="creating">
        {{ creating ? 'Creating…' : 'Create Staff' }}
      </button>
      <div v-if="createError" class="alert alert-danger py-2 small mt-2 mb-0">{{ createError }}</div>
    </form>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading staff…</p>

    <table v-else-if="staff.length" class="table table-striped align-middle">
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="member in staff" :key="member.id">
          <template v-if="editingId === member.id">
            <td><input v-model="editForm.full_name" type="text" class="form-control form-control-sm" /></td>
            <td>{{ member.email }}</td>
            <td><input v-model="editForm.phone" type="text" class="form-control form-control-sm" /></td>
            <td>
              <span class="badge" :class="member.active ? 'bg-success' : 'bg-secondary'">
                {{ member.active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="text-nowrap">
              <button type="button" class="btn btn-sm btn-outline-primary me-1" @click="saveEdit(member)">Save</button>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="cancelEdit">Cancel</button>
            </td>
          </template>
          <template v-else>
            <td>{{ member.name }}</td>
            <td>{{ member.email }}</td>
            <td>{{ member.phone_number }}</td>
            <td>
              <span class="badge" :class="member.active ? 'bg-success' : 'bg-secondary'">
                {{ member.active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="text-nowrap">
              <button type="button" class="btn btn-sm btn-outline-secondary me-1" @click="startEdit(member)">
                Edit
              </button>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleActive(member)">
                {{ member.active ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </template>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-muted">No staff found.</p>
  </div>
</template>
