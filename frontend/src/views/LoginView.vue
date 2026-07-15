<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { dashboardPathFor } from '@/router'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push(dashboardPathFor(auth.role))
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-12 col-sm-8 col-md-5 col-lg-4">
        <form class="card mt-5 p-4" @submit.prevent="handleLogin">
          <h1 class="h4 mb-1">Log in</h1>
          <p class="text-muted small mb-3">Welcome back to GoTrek</p>

          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              class="form-control"
              required
              placeholder="you@example.com"
              autocomplete="email"
            />
          </div>

          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              class="form-control"
              required
              placeholder="********"
              autocomplete="current-password"
            />
          </div>

          <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>

          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? 'Logging in…' : 'Log in' }}
          </button>

          <p class="text-center small mt-3 mb-0">
            Don't have an account?
            <RouterLink to="/signup">Sign up</RouterLink>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>
