// UserGuide.vue
<script setup>
import { ref, onMounted } from "vue";
import { request } from "@/utils/request";

const guide = ref("");
const loading = ref(true);

onMounted(async () => {
  try {
    const data = await request("/api/frontend-settings");
    guide.value = data.user_guide;
  } catch (err) {
    console.error("Error:", err);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div v-if="loading" class="flex justify-center">
      <div
        class="animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent"
      ></div>
    </div>
    <div v-else class="prose max-w-none" v-html="guide"></div>
  </div>
</template>
