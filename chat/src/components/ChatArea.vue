<template>
  <div class="flex-1 flex flex-col pt-16">
    <MessageList :messages="messages" />
    <MessageInput
      :modelValue="modelValue"
      @update:modelValue="$emit('update:modelValue', $event)"
      :filePreviews="filePreviews"
      :showAttachButton="true"
      :maxFiles="3"
      @send="$emit('send')"
      @fileSelect="$emit('fileSelect', $event)"
      @paste="$emit('paste', $event)"
      @drop="$emit('drop', $event)"
    />
  </div>
</template>

<script setup>
import MessageList from "./MessageList.vue";
import MessageInput from "./MessageInput.vue";

defineProps(["messages", "filePreviews", "modelValue"]);
defineEmits(["update:modelValue", "send", "fileSelect", "paste", "drop"]);
</script>
