<script setup>
import AppNav from '@/components/AppNav.vue'
import AdminNav from '@/components/admin/AdminNav.vue'
import UserSection from '@/components/admin/UserSection.vue'
</script>

<template>
  <AppNav />
  <div class="container my-4">
    <AdminNav />
    <UserSection />
  </div>
</template>

