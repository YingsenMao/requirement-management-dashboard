<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="logo-wrapper">
        <!-- Use absolute path to reference the public directory -->
        <img src="/Yuwell.jpg" alt="Yuwell Logo" class="login-logo" />
      </div>
      <el-form @submit.prevent="handleLogin" :model="form" label-position="top">
        <el-form-item label="Username">
          <el-input v-model="form.username" placeholder="Enter username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" placeholder="Enter password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" class="login-submit">
            Login
          </el-button>
        </el-form-item>
        <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon :closable="false" class="login-alert" />
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    errorMsg.value = 'Please enter both username and password.'
    return
  }

  loading.value = true
  errorMsg.value = ''

  const success = await authStore.login(form.value.username, form.value.password)
  loading.value = false

  if (success) {
    if (authStore.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/user')
    }
  } else {
    errorMsg.value = 'Invalid username or password.'
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  background-color: var(--color-surface-auth);
  box-sizing: border-box;
}

.login-card {
  width: var(--layout-login-card-width);
}

.logo-wrapper {
  text-align: center;
}

.login-logo {
  max-width: var(--layout-login-logo-max);
  height: auto;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.login-submit {
  width: 100%;
}

.login-alert {
  margin-top: var(--space-2);
}
</style>
