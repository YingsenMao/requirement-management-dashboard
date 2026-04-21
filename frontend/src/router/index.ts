import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/user',
      name: 'UserDashboard',
      component: () => import('../views/UserDashboard.vue'),
      meta: { requiresAuth: true, role: 'user' }
    },
    {
      path: '/admin',
      name: 'AdminDashboard',
      component: () => import('../views/AdminDashboard.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/',
      redirect: '/login'
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = !!authStore.token
  const userRole = authStore.role

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.role && to.meta.role !== userRole) {
    if (userRole === 'admin') next({ name: 'AdminDashboard' })
    else if (userRole === 'user') next({ name: 'UserDashboard' })
    else next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
