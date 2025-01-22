<template>
  <div class="h-[10%] p-4">
    <div class="flex flex-col space-y-2">
      <a
        href="https://github.com/cchking/ytbox"
        target="_blank"
        rel="noopener noreferrer"
      >
        <img src="@/assets/images/UilGithub.svg" alt="GitHub" class="w-6 h-6" />
      </a>
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
  </div>
</template>

<script setup>
defineProps(["colors"]);
defineEmits(["change"]);
</script>
