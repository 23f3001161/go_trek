import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import IndexView from '@/views/IndexView.vue'

import AdminDashboardPage from '@/views/admin/DashboardPage.vue'
import AdminStaffPage from '@/views/admin/StaffPage.vue'
import AdminTreksPage from '@/views/admin/TreksPage.vue'
import AdminUsersPage from '@/views/admin/UsersPage.vue'
import AdminBookingsPage from '@/views/admin/BookingsPage.vue'

import StaffTreksPage from '@/views/staff/TreksPage.vue'
import StaffParticipantsPage from '@/views/staff/ParticipantsPage.vue'

import UserDashboardPage from '@/views/user/DashboardPage.vue'
import UserBrowseTreksPage from '@/views/user/BrowseTreksPage.vue'
import UserBookingsPage from '@/views/user/BookingsPage.vue'
import UserBookingDetailPage from '@/views/user/BookingDetailPage.vue'
import UserHistoryPage from '@/views/user/HistoryPage.vue'
import UserProfilePage from '@/views/user/ProfilePage.vue'


export function dashboardPathFor(roles) {
  if (roles?.includes('admin')) return '/admin'
  if (roles?.includes('staff')) return '/staff'
  if (roles?.includes('user')) return '/user'
  return '/'
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: IndexView,
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('../views/SignupView.vue'),
      meta: { guestOnly: true },
    },


    { path: '/admin', component: AdminDashboardPage, meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/admin/staff', component: AdminStaffPage, meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/admin/treks', component: AdminTreksPage, meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/admin/users', component: AdminUsersPage, meta: { requiresAuth: true, roles: ['admin'] } },
    { path: '/admin/bookings', component: AdminBookingsPage, meta: { requiresAuth: true, roles: ['admin'] } },

    // Staff — assigned treks list, drilling into a per-trek participants page.
    { path: '/staff', component: StaffTreksPage, meta: { requiresAuth: true, roles: ['staff'] } },
    {
      path: '/staff/treks/:id',
      component: StaffParticipantsPage,
      meta: { requiresAuth: true, roles: ['staff'] },
    },


    { path: '/user', component: UserDashboardPage, meta: { requiresAuth: true, roles: ['user'] } },
    { path: '/user/treks', component: UserBrowseTreksPage, meta: { requiresAuth: true, roles: ['user'] } },
    { path: '/user/bookings', component: UserBookingsPage, meta: { requiresAuth: true, roles: ['user'] } },
    {
      path: '/user/bookings/:id',
      component: UserBookingDetailPage,
      meta: { requiresAuth: true, roles: ['user'] },
    },
    { path: '/user/history', component: UserHistoryPage, meta: { requiresAuth: true, roles: ['user'] } },
    { path: '/user/profile', component: UserProfilePage, meta: { requiresAuth: true, roles: ['user'] } },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()


  if (to.meta.guestOnly && auth.token) {
    return dashboardPathFor(auth.role)
  }


  if (to.meta.requiresAuth && !auth.token) {
    return '/login'
  }

  if (to.meta.roles && !to.meta.roles.some((r) => auth.role?.includes(r))) {
    return dashboardPathFor(auth.role)
  }
})

export default router