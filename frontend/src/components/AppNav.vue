<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { dashboardPathFor } from '@/router'

const auth = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light border-bottom">
    <div class="container-fluid">
      <RouterLink :to="dashboardPathFor(auth.role)" class="navbar-brand">GoTrek</RouterLink>
      <div class="d-flex align-items-center ms-auto">
        <span class="me-2">{{ auth.name }}</span>
        <span class="badge bg-secondary me-3 text-capitalize">{{ auth.role?.join(', ') }}</span>
        <button type="button" class="btn btn-outline-secondary btn-sm" @click="handleLogout">
          Log out
        </button>
      </div>
    </div>
  </nav>
</template>
