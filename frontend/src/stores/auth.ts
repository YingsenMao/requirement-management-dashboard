import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const role = ref<string | null>(localStorage.getItem('user_role'))
  const username = ref<string | null>(localStorage.getItem('username'))

  const login = async (usernameInput: string, passwordInput: string) => {
    try {
      const response = await axios.post('/api/token/', {
        username: usernameInput,
        password: passwordInput
      })
      token.value = response.data.access
      refreshToken.value = response.data.refresh
      
      const payload = JSON.parse(atob(response.data.access.split('.')[1]))
      role.value = payload.role
      username.value = payload.username

      localStorage.setItem('access_token', token.value!)
      localStorage.setItem('refresh_token', refreshToken.value!)
      localStorage.setItem('user_role', role.value!)
      localStorage.setItem('username', username.value!)
      
      return true
    } catch (error) {
      console.error('Login failed', error)
      return false
    }
  }

  const logout = () => {
    token.value = null
    refreshToken.value = null
    role.value = null
    username.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('username')
  }

  return { token, refreshToken, role, username, login, logout }
})
