<template>
  <div class="flex space-x-2">
    <div
      v-for="index in 3"
      :key="index"
      :class="[
        'w-3 h-3 rounded-full transition-colors duration-300',
        getDotColor(index - 1),
      ]"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const position = ref(0);
const isForward = ref(true);
let interval = null;

const getDotColor = (index) => {
  if (index === position.value) return "bg-indigo-600";

  if (isForward.value) {
    if (index < position.value) return "bg-indigo-400";
    return "bg-gray-300";
  } else {
    if (index > position.value) return "bg-indigo-400";
    return "bg-gray-300";
  }
};

onMounted(() => {
  interval = setInterval(() => {
    position.value = (() => {
      if (position.value === 2 && isForward.value) {
        isForward.value = false;
        return 1;
      }
      if (position.value === 0 && !isForward.value) {
        isForward.value = true;
        return 1;
      }
      return isForward.value ? position.value + 1 : position.value - 1;
    })();
  }, 500);
});

onUnmounted(() => {
  if (interval) clearInterval(interval);
});
</script>
