<!-- src/components/FileUpload.vue -->
<template>
  <div @click="triggerFileInput">
    <input
      type="file"
      ref="fileInput"
      @change="handleFileChange"
      accept="image/*,.txt,.doc,.docx,.pdf"
      :multiple="maxFiles !== 1"
      class="hidden"
    />
    <slot>
      <button
        type="button"
        class="p-2 text-gray-500 hover:bg-gray-200 rounded-lg"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"
          />
        </svg>
      </button>
    </slot>
  </div>
</template>

<script setup>
import { ref } from "vue";

const fileInput = ref(null);

const props = defineProps({
  maxFiles: {
    type: Number,
    default: null,
  },
});

const emit = defineEmits(["select"]);

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileChange = (event) => {
  if (event.target.files) {
    if (props.maxFiles && event.target.files.length > props.maxFiles) {
      alert(`最多只能选择 ${props.maxFiles} 个文件`);
      event.target.value = "";
      return;
    }
    emit("select", event.target.files);
    event.target.value = "";
  }
};
</script>
