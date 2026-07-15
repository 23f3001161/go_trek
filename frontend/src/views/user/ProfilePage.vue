<script setup>
import { ref } from 'vue'
import AppNav from '@/components/AppNav.vue'
import UserNav from '@/components/user/UserNav.vue'
import { apiFetch } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()


const form = ref({ full_name: auth.name || '', email: auth.email || '', phone: '' })
const saving = ref(false)
const error = ref('')
const success = ref('')

async function saveProfile() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
  
    const payload = Object.fromEntries(Object.entries(form.value).filter(([, v]) => v))
    const data = await apiFetch('/api/users/profile', {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
    auth.updateProfile({ name: data.data.name, email: data.data.email })
    success.value = 'Profile updated.'
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <AppNav />
  <div class="container my-4" style="max-width: 450px">
    <UserNav />
    <h1 class="h4 mb-3">Profile</h1>

    <form class="card card-body" @submit.prevent="saveProfile">
      <div class="mb-3">
        <label for="full_name" class="form-label">Full name</label>
        <input id="full_name" v-model="form.full_name" type="text" class="form-control" />
      </div>

      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input id="email" v-model="form.email" type="email" class="form-control" />
      </div>

      <div class="mb-3">
        <label for="phone" class="form-label">Phone</label>
        <input
          id="phone"
          v-model="form.phone"
          type="text"
          class="form-control"
          placeholder="Leave blank to keep unchanged"
        />
      </div>

      <div v-if="success" class="alert alert-success py-2 small">{{ success }}</div>
      <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>

      <button type="submit" class="btn btn-primary" :disabled="saving">
        {{ saving ? 'Saving…' : 'Save changes' }}
      </button>
    </form>
  </div>
</template>
