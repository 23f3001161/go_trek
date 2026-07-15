<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/lib/api'

const users = ref([])
const search = ref('')

const statusFilter = ref('')
const staffOnly = ref(false)
const loading = ref(false)
const error = ref('')

const editingId = ref(null)
const editForm = ref({ full_name: '', phone: '' })

async function loadUsers() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('q', search.value)
    params.set('status', statusFilter.value)
    if (staffOnly.value) params.set('staff', 'true')
    const data = await apiFetch(`/api/users?${params.toString()}`)
    users.value = data.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function toggleActive(user) {
  try {
    await apiFetch(`/api/users/${user.id}`, {
      method: 'PUT',
      body: JSON.stringify({ active: !user.active }),
    })
    user.active = !user.active
  } catch (err) {
    error.value = err.message
  }
}

function startEdit(user) {
  editingId.value = user.id
  editForm.value = { full_name: user.name, phone: user.phone_number }
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(user) {
  try {
    await apiFetch(`/api/users/${user.id}`, {
      method: 'PUT',
      body: JSON.stringify(editForm.value),
    })
    user.name = editForm.value.full_name
    user.phone_number = editForm.value.phone
    editingId.value = null
  } catch (err) {
    error.value = err.message
  }
}

onMounted(loadUsers)
</script>

<template>
  <div>
    <div class="d-flex align-items-center gap-2 mb-3 flex-wrap">
      <input
        v-model="search"
        type="text"
        class="form-control"
        style="max-width: 260px"
        placeholder="Search by name, email, or phone…"
        @keyup.enter="loadUsers"
      />
      <select v-model="statusFilter" class="form-select" style="max-width: 150px" @change="loadUsers">
        <option value="">All</option>
        <option value="true">Active</option>
        <option value="false">Inactive</option>
      </select>
      <div class="form-check">
        <input id="staffOnly" v-model="staffOnly" class="form-check-input" type="checkbox" @change="loadUsers" />
        <label class="form-check-label" for="staffOnly">Staff only</label>
      </div>
      <button type="button" class="btn btn-outline-secondary" @click="loadUsers">Search</button>
    </div>

    <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
    <p v-if="loading">Loading users…</p>

    <table v-else-if="users.length" class="table table-striped align-middle">
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Roles</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <template v-if="editingId === user.id">
            <td><input v-model="editForm.full_name" type="text" class="form-control form-control-sm" /></td>
            <td>{{ user.email }}</td>
            <td><input v-model="editForm.phone" type="text" class="form-control form-control-sm" /></td>
            <td>
              <span v-for="r in user.roles" :key="r" class="badge bg-secondary me-1">{{ r }}</span>
            </td>
            <td>
              <span class="badge" :class="user.active ? 'bg-success' : 'bg-secondary'">
                {{ user.active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="text-nowrap">
              <button type="button" class="btn btn-sm btn-outline-primary me-1" @click="saveEdit(user)">Save</button>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="cancelEdit">Cancel</button>
            </td>
          </template>
          <template v-else>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.phone_number }}</td>
            <td>
              <span v-for="r in user.roles" :key="r" class="badge bg-secondary me-1">{{ r }}</span>
            </td>
            <td>
              <span class="badge" :class="user.active ? 'bg-success' : 'bg-secondary'">
                {{ user.active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="text-nowrap">
              <button type="button" class="btn btn-sm btn-outline-secondary me-1" @click="startEdit(user)">
                Edit
              </button>
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleActive(user)">
                {{ user.active ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </template>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-muted">No users found.</p>
  </div>
</template>
