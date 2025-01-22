<!-- src/components/ThemeSection.vue -->
<template>
  <div class="h-[10%] p-4">
    <h2 class="text-xl font-bold mb-2">样式</h2>
    <div class="flex space-x-2">
      <button
        v-for="color in colors"
        :key="color"
        class="w-8 h-8 rounded-full"
        :class="`bg-${color}-500`"
        @click="$emit('change', color)"
      ></button>
    </div>
  </div>
</template>

<script setup>
defineProps(["colors"]);
defineEmits(["change"]);
</script>
