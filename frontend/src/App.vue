<template>
  <el-container style="height: 100vh;">
    <el-header v-if="!route.meta.hideHeader" style="display: flex; align-items: center; margin: 15px">
      <div class="logo-wrapper">
        <!-- Use absolute path to reference the public directory -->
        <img src="/Yuwell.jpg" alt="Yuwell Logo" class="login-logo" />
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

.logo-wrapper {
  text-align: center;
  margin: 10px;
}