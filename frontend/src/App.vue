<template>
  <el-container class="app-layout">
    <el-header v-if="!route.meta.hideHeader" class="app-header">
      <div class="logo-wrapper">
        <!-- Use absolute path to reference the public directory -->
        <img src="/Yuwell.jpg" alt="Yuwell Logo" class="app-header-logo" />
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<style scoped>
.app-layout {
  height: var(--layout-viewport-height);
}

.app-header {
  display: flex;
  align-items: center;
  margin: var(--space-header);
}

.logo-wrapper {
  text-align: center;
  margin: var(--space-2);
}

.app-header-logo {
  max-height: 48px;
  width: auto;
  object-fit: contain;
  display: block;
}

.app-main {
  padding: 0;
}
</style>
