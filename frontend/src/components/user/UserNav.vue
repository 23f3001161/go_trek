<script setup>
const links = [
  { to: '/user', label: 'Dashboard' },
  { to: '/user/treks', label: 'Browse Treks' },
  { to: '/user/bookings', label: 'My Bookings' },
  { to: '/user/history', label: 'History' },
  { to: '/user/profile', label: 'Profile' },
]
</script>

<template>
  <ul class="nav nav-tabs mb-4">
    <li v-for="link in links" :key="link.to" class="nav-item">
      <RouterLink :to="link.to" class="nav-link" exact-active-class="active">{{ link.label }}</RouterLink>
    </li>
  </ul>
</template>
