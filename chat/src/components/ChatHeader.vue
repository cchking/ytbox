<template>
  <div
    class="fixed top-0 right-0 h-16 bg-white shadow-md z-10 transition-all duration-200"
    :style="{ left: isMobile ? '0' : `${sidebarWidth}px` }"
  >
    <div
      class="h-full flex items-center"
      :class="{
        'justify-center': isMobile,
        'justify-start px-4': !isMobile,
      }"
    >
      <!-- 模型选择器 -->
      <ModelSelector
        :currentModel="currentModel"
        :models="models"
        @select="$emit('select', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import ModelSelector from "./ModelSelector.vue";

const props = defineProps({
  currentModel: {
    type: Object,
    required: true,
  },
  models: {
    type: Array,
    required: true,
  },
  sidebarWidth: {
    type: Number,
    default: 320,
  },
  isMobile: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["select"]);
</script>
