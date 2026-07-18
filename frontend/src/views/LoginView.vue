<template>
  <div class="login-page">
    <div class="brand-panel">
      <div class="brand-content">
        <img src="/Yuwell.jpg" alt="Yuwell" class="brand-logo" />
        <h1 class="brand-title">Requirement Management</h1>
        <p class="brand-tagline">Collect, prioritize and deliver what matters most.</p>
      </div>
      <div class="brand-decoration">
        <div class="deco-circle deco-circle-1"></div>
        <div class="deco-circle deco-circle-2"></div>
        <div class="deco-circle deco-circle-3"></div>
      </div>
    </div>
    <div class="form-panel">
      <div class="form-card">
        <h2 class="form-title">Welcome Back</h2>
        <p class="form-subtitle">Sign in to your account</p>
        <transition name="alert-fade">
          <el-alert
            v-if="errorMsg"
            :title="errorMsg"
            type="error"
            show-icon
            :closable="false"
            class="form-alert"
          />
        </transition>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleLogin"
          label-position="top"
          size="large"
        >
          <el-form-item label="Username" prop="username">
            <el-input
              v-model="form.username"
              placeholder="Enter your username"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item label="Password" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="Enter your password"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>
          <el-form-item class="submit-item">
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              class="login-submit"
            >
              Sign In
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')

const rules: FormRules = {
  username: [{ required: true, message: 'Please enter your username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter your password', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    errorMsg.value = ''
    const success = await authStore.login(form.value.username, form.value.password)
    loading.value = false
    if (success) {
      router.push(authStore.role === 'admin' ? '/admin' : '/user')
    } else {
      errorMsg.value = 'Invalid username or password.'
    }
  })
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  width: 100%;
}

.brand-panel {
  flex: 1;
  background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 60%, #3b82f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: var(--space-6);
}

.brand-content {
  position: relative;
  z-index: 2;
  text-align: center;
  color: var(--color-text-inverse);
}

.brand-logo {
  width: 140px;
  height: auto;
  object-fit: contain;
  margin-bottom: var(--space-5);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.15);
  padding: var(--space-3);
  backdrop-filter: blur(8px);
}

.brand-title {
  font-size: 28px;
  font-weight: var(--font-weight-title);
  margin: 0 0 var(--space-2);
  letter-spacing: -0.5px;
}

.brand-tagline {
  font-size: 15px;
  opacity: 0.85;
  margin: 0;
  font-weight: 400;
}

.brand-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}

.deco-circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
}

.deco-circle-2 {
  width: 250px;
  height: 250px;
  bottom: -60px;
  left: -60px;
  background: rgba(255, 255, 255, 0.07);
}

.deco-circle-3 {
  width: 150px;
  height: 150px;
  bottom: 30%;
  right: 15%;
  background: rgba(255, 255, 255, 0.04);
}

.form-panel {
  width: 480px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-card);
  padding: var(--space-6);
}

.form-card {
  width: 100%;
  max-width: 380px;
}

.form-title {
  font-size: 26px;
  font-weight: var(--font-weight-title);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1);
}

.form-subtitle {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0 0 var(--space-5);
}

.form-alert {
  margin-bottom: var(--space-3);
}

.submit-item {
  margin-bottom: 0;
}

.login-submit {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-md);
}

.alert-fade-enter-active {
  transition: all 0.25s ease-out;
}

.alert-fade-leave-active {
  transition: all 0.15s ease-in;
}

.alert-fade-enter-from,
.alert-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 900px) {
  .brand-panel {
    display: none;
  }
  .form-panel {
    width: 100%;
  }
}
</style>
