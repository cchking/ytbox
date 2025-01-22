<!-- src/components/FilePreview.vue -->
<template>
  <div class="mb-4 flex flex-wrap gap-2">
    <div v-for="file in files" :key="file.id" class="relative">
      <div
        v-if="file.type === 'image'"
        class="w-24 h-24 rounded-lg overflow-hidden"
      >
        <img
          :src="file.url"
          :alt="file.name"
          class="w-full h-full object-cover"
        />
        <button
          @click="$emit('remove', file.id)"
          class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full text-white"
        >
          ×
        </button>
      </div>
      <div v-else class="p-3 bg-gray-100 rounded-lg">
        <button
          @click="$emit('remove', file.id)"
          class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full text-white"
        >
          ×
        </button>
        <div class="flex items-center gap-2">
          <i class="fas fa-file-alt text-gray-500"></i>
          <span class="text-sm truncate max-w-[120px]">{{ file.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps(["files"]);
defineEmits(["remove"]);
</script>
