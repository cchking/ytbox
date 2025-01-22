// src/components/ui/dialog/DialogTitle.vue
<template>
  <DialogTitle as="h3" class="text-lg font-semibold">
    <slot />
  </DialogTitle>
</template>

<script setup>
import { DialogTitle } from "@headlessui/vue";
</script>
