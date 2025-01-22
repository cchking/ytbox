// src/components/ui/dialog/Dialog.vue
<template>
  <TransitionRoot appear :show="open" as="template">
    <Dialog as="div" class="relative z-50" @close="$emit('close')">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <slot />
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { Dialog, DialogPanel, TransitionRoot, TransitionChild } from '@headlessui/vue'

defineProps({
  open: {
    type: Boolean,
    required: true
  }
})

defineEmits(['close'])
</script>

// src/components/ui/dialog/DialogContent.vue
<template>
  <div class="relative bg-white">
    <slot />
  </div>
</template>

// src/components/ui/dialog/DialogHeader.vue
<template>
  <div class="flex flex-col space-y-1.5 pb-2">
    <slot />
  </div>
</template>

// src/components/ui/dialog/DialogTitle.vue
<template>
  <DialogTitle as="h3" class="text-lg font-semibold">
    <slot />
  </DialogTitle>
</template>

<script setup>
import { DialogTitle } from '@headlessui/vue'
</script>

// src/components/ui/dialog/DialogFooter.vue
<template>
  <div class="flex justify-end space-x-2">
    <slot />
  </div>
</template>

// src/components/ui/dialog/index.js
export { default as Dialog } from './Dialog.vue'
export { default as DialogContent } from './DialogContent.vue'
export { default as DialogHeader } from './DialogHeader.vue'
export { default as DialogTitle } from './DialogTitle.vue'
export { default as DialogFooter } from './DialogFooter.vue'