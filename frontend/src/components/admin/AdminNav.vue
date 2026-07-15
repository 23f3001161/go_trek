<script setup>
const links = [
  { to: '/admin', label: 'Dashboard' },
  { to: '/admin/staff', label: 'Staff' },
  { to: '/admin/treks', label: 'Treks' },
  { to: '/admin/users', label: 'Users' },
  { to: '/admin/bookings', label: 'Bookings' },
]
</script>

<template>
  <ul class="nav nav-tabs mb-4">
    <li v-for="link in links" :key="link.to" class="nav-item">
      <RouterLink :to="link.to" class="nav-link" active-class="active">{{ link.label }}</RouterLink>
    </li>
  </ul>
</template>