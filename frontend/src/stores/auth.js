import { ref, computed } from 'vue'
import { defineStore } from 'pinia'


export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('auth_token') || null)
  const id = ref(Number(localStorage.getItem('auth_id')) || null)
  const name = ref(localStorage.getItem('auth_name') || null)
  const email = ref(localStorage.getItem('auth_email') || null)
  const role = ref(JSON.parse(localStorage.getItem('auth_role') || '[]'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => role.value?.includes('admin'))
  const isStaff = computed(() => role.value?.includes('staff'))
  const isUser = computed(() => role.value?.includes('user'))

  async function login(loginEmail, password) {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: loginEmail, password }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || data.message || 'Login failed')

    token.value = data.auth_token
    id.value = data.data.id
    name.value = data.data.name
    role.value = data.data.role

    email.value = loginEmail

    localStorage.setItem('auth_token', token.value)
    localStorage.setItem('auth_id', id.value)
    localStorage.setItem('auth_name', name.value)
    localStorage.setItem('auth_email', email.value)
    localStorage.setItem('auth_role', JSON.stringify(role.value))
  }

  async function register(fullName, registerEmail, password) {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: fullName, email: registerEmail, password }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.message || data.error || 'Registration failed')
    return data
  }

  async function logout() {
    if (token.value) {
      await fetch('/api/logout', {
        method: 'POST',
        headers: { 'Authentication-Token': token.value },
      }).catch(() => {})
    }
    token.value = null
    id.value = null
    name.value = null
    email.value = null
    role.value = null

    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_id')
    localStorage.removeItem('auth_name')
    localStorage.removeItem('auth_email')
    localStorage.removeItem('auth_role')
  }


  function updateProfile({ name: newName, email: newEmail }) {
    if (newName) {
      name.value = newName
      localStorage.setItem('auth_name', newName)
    }
    if (newEmail) {
      email.value = newEmail
      localStorage.setItem('auth_email', newEmail)
    }
  }

  return {
    token,
    id,
    name,
    email,
    role,
    isAuthenticated,
    isAdmin,
    isStaff,
    isUser,
    login,
    register,
    logout,
    updateProfile,
  }
})
