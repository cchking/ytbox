<!-- src/components/SendButton.vue -->
<template>
  <button
    class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
    @click="$emit('click')"
  >
    <i class="fas fa-paper-plane"></i>
  </button>
</template>

<script setup>
defineEmits(["click"]);
</script>
