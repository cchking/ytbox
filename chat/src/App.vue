<!-- src/App.vue -->
<template>
  <router-view></router-view>
</template>

<script setup>
import { onMounted } from "vue";
import { useSettingsStore } from "@/stores/settings";

const settingsStore = useSettingsStore();

// 在组件挂载时获取设置
onMounted(() => {
  settingsStore.fetchSettings();
});
</script>
