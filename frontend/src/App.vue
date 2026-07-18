<template>
  <div class="app-root">
    <nav v-if="authStore.token" class="navbar">
      <div class="navbar-inner">
        <div class="navbar-brand">
          <img src="/Yuwell.jpg" alt="Yuwell" class="navbar-logo" />
          <span class="navbar-title">Requirement Management</span>
        </div>
        <div class="navbar-actions">
          <div class="navbar-user">
            <el-avatar :size="32" class="user-avatar">
              {{ authStore.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="user-info">
              <span class="user-name">{{ authStore.username }}</span>
              <span class="user-role">{{ authStore.role === 'admin' ? 'Admin' : 'User' }}</span>
            </div>
          </div>
          <el-button text @click="handleLogout" class="logout-btn">
            <el-icon><SwitchButton /></el-icon>
          </el-button>
        </div>
      </div>
    </nav>
    <main class="app-main" :class="{ 'no-navbar': !authStore.token }">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-root {
  min-height: var(--layout-viewport-height);
  display: flex;
  flex-direction: column;
}

.navbar {
  height: var(--layout-navbar-height);
  background: var(--color-surface-navbar);
  border-bottom: 1px solid var(--color-border-default);
  box-shadow: var(--shadow-navbar);
  flex-shrink: 0;
  z-index: 100;
}

.navbar-inner {
  max-width: 1440px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-5);
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.navbar-logo {
  height: 34px;
  width: auto;
  object-fit: contain;
}

.navbar-title {
  font-size: var(--font-size-brand);
  font-weight: var(--font-weight-title);
  color: var(--color-text-primary);
  letter-spacing: -0.3px;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.user-avatar {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.user-name {
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--color-text-muted);
}

.logout-btn {
  color: var(--color-text-muted);
  font-size: 18px;
}

.logout-btn:hover {
  color: var(--color-text-primary);
}

.app-main {
  flex: 1;
  overflow-y: auto;
}
</style>
