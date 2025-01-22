<template>
  <div
    class="fixed bottom-0 w-full"
    :style="{
      left: isMobile ? '0' : `${sidebarWidth}px`,
      width: isMobile ? '100%' : `calc(100% - ${sidebarWidth}px)`,
    }"
  >
    <div class="mx-auto w-full md:w-[60%] max-w-3xl p-4">
      <div class="relative border rounded-2xl bg-white shadow-sm">
        <FilePreview
          v-if="filePreviews.length"
          :files="filePreviews"
          @remove="$emit('removeFile', $event)"
        />

        <textarea
          v-model="message"
          ref="messageInput"
          class="w-full px-4 py-3 resize-none focus:outline-none rounded-t-2xl overflow-auto"
          :style="{
            height: Math.min(textareaHeight, maxHeight) + 'px',
            maxHeight: maxHeight + 'px',
          }"
          :placeholder="placeholder"
          @input="adjustHeight"
          @keydown.enter.exact.prevent="handleEnter"
          @keydown.ctrl.enter="handleSend"
          @paste="handlePaste"
          @drop.prevent="handleDrop"
          @dragover.prevent
        ></textarea>

        <div class="flex items-center justify-between px-4 pt-2 pb-3">
          <div class="flex items-center gap-2">
            <div
              class="flex items-center text-blue-600 border rounded-full px-2 py-0.5 bg-blue-50"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="mr-1"
              >
                <path
                  d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"
                ></path>
                <path
                  d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"
                ></path>
              </svg>
              <span class="text-sm">{{ mode }}</span>
            </div>

            <div v-if="showWordCount" class="text-sm text-gray-500">
              {{ message?.length || 0 }}/{{ maxLength }}
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              v-if="showEmojiButton"
              class="p-2 text-gray-500 hover:text-gray-700 transition-colors"
              @click="toggleEmojiPicker"
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
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
                <line x1="9" y1="9" x2="9.01" y2="9"></line>
                <line x1="15" y1="9" x2="15.01" y2="9"></line>
              </svg>
            </button>

            <FileUpload
              v-if="showAttachButton"
              :maxFiles="maxFiles"
              @select="handleFileSelect"
            >
              <button
                class="p-2 text-gray-500 hover:text-gray-700 transition-colors"
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
                  ></path>
                </svg>
              </button>
            </FileUpload>

            <template v-if="canSend || isGenerating">
              <button
                v-if="!isGenerating"
                class="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors"
                @click="handleSend"
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
                  <path d="m6 12 6-6 6 6"></path>
                  <path d="M12 18V6"></path>
                </svg>
              </button>
              <button
                v-else
                class="relative bg-black text-white p-2.5 rounded-full hover:bg-gray-900 transition-colors"
                @click="$emit('stop')"
              >
                <!-- 调整白色方块的圆角，从 rounded-lg 改为具体的像素值 -->
                <div class="w-3.5 h-3.5 bg-white rounded-sm"></div>

                <!-- 波纹动画 -->
                <div class="absolute inset-0">
                  <div
                    class="absolute inset-0 rounded-full animate-pulse-wave"
                  ></div>
                </div>
              </button>
            </template>
          </div>
        </div>

        <div
          v-if="showEmojiPicker"
          class="absolute bottom-full mb-2 right-0 bg-white rounded-lg shadow-lg p-2"
        >
          <div class="grid grid-cols-8 gap-1">
            <button
              v-for="emoji in commonEmojis"
              :key="emoji"
              class="p-1 hover:bg-gray-100 rounded"
              @click="insertEmoji(emoji)"
            >
              {{ emoji }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import FilePreview from "./FilePreview.vue";
import FileUpload from "./FileUpload.vue";

const props = defineProps({
  modelValue: String,
  filePreviews: {
    type: Array,
    default: () => [],
  },
  showAttachButton: {
    type: Boolean,
    default: true,
  },
  showEmojiButton: {
    type: Boolean,
    default: true,
  },
  showWordCount: {
    type: Boolean,
    default: true,
  },
  maxLength: {
    type: Number,
    default: 100000,
  },
  maxFiles: Number,
  mode: {
    type: String,
    default: "Concise",
  },
  placeholder: {
    type: String,
    default: "输入消息... (Ctrl + Enter 发送)",
  },
  sidebarWidth: {
    type: Number,
    default: 320,
  },
  isMobile: {
    // 添加 isMobile 属性
    type: Boolean,
    default: false,
  },
  isGenerating: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "update:modelValue",
  "send",
  "stop",
  "fileSelect",
  "paste",
  "drop",
  "removeFile",
]);

const messageInput = ref(null);
const textareaHeight = ref(56);
const showEmojiPicker = ref(false);
const commonEmojis = [
  "😊",
  "😂",
  "🤔",
  "👍",
  "❤️",
  "🎉",
  "🔥",
  "✨",
  "🙏",
  "👏",
  "😎",
  "🤗",
  "😄",
  "😃",
  "😅",
  "😉",
];

const maxHeight = computed(() => Math.floor(window.innerHeight * 0.3));

const message = computed({
  get: () => props.modelValue,
  set: (val) => {
    if (!props.maxLength || val.length <= props.maxLength) {
      emit("update:modelValue", val);
    }
  },
});

const canSend = computed(() => {
  const hasText = message.value && message.value.trim().length > 0;
  const hasFiles = props.filePreviews && props.filePreviews.length > 0;
  return hasText || hasFiles;
});
const adjustHeight = async () => {
  await nextTick();
  const textarea = messageInput.value;
  if (textarea) {
    const scrollTop = textarea.scrollTop;
    textarea.style.height = "56px";
    const scrollHeight = textarea.scrollHeight;
    const lineCount = textarea.value.split("\n").length;
    const lineHeight = 24;
    const contentHeight = Math.max(56, lineCount * lineHeight, scrollHeight);
    textarea.style.height = contentHeight + "px";
    textareaHeight.value = contentHeight;
    textarea.scrollTop = scrollTop;
  }
};

const handleEnter = (e) => {
  if (!e.shiftKey) {
    message.value = message.value + "\n";
    adjustHeight();
  }
};

const handleSend = () => {
  if (canSend.value) {
    emit("send");
    showEmojiPicker.value = false;
  }
};

const handleFileSelect = (files) => {
  emit("fileSelect", files);
  showEmojiPicker.value = false;
};

const handlePaste = (e) => {
  emit("paste", e);
  showEmojiPicker.value = false;
};

const handleDrop = (e) => {
  emit("drop", e);
  showEmojiPicker.value = false;
};

const toggleEmojiPicker = () => {
  showEmojiPicker.value = !showEmojiPicker.value;
};

const insertEmoji = (emoji) => {
  const textarea = messageInput.value;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const text = message.value || "";
  message.value = text.substring(0, start) + emoji + text.substring(end);
  nextTick(() => {
    textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
    textarea.focus();
  });
};

const handleClickOutside = (event) => {
  const picker = document.querySelector(".emoji-picker");
  if (picker && !picker.contains(event.target)) {
    showEmojiPicker.value = false;
  }
};

watch(() => message.value, adjustHeight);

onMounted(() => {
  adjustHeight();
  window.addEventListener("resize", adjustHeight);
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  window.removeEventListener("resize", adjustHeight);
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
textarea {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 transparent;
}

textarea::-webkit-scrollbar {
  width: 8px;
}

textarea::-webkit-scrollbar-track {
  background: transparent;
}

textarea::-webkit-scrollbar-thumb {
  background-color: #cbd5e0;
  border-radius: 4px;
  border: 2px solid transparent;
}

.emoji-picker {
  max-height: 200px;
  overflow-y: auto;
}
@keyframes pulse-wave {
  0% {
    transform: scale(1);
    opacity: 0.7;
    background: linear-gradient(135deg, #4b0082, #000000);
  }
  50% {
    transform: scale(1.6);
    opacity: 0.2;
    background: linear-gradient(135deg, #4b0082, #000000);
  }
  100% {
    transform: scale(1);
    opacity: 0.7;
    background: linear-gradient(135deg, #4b0082, #000000);
  }
}

.animate-pulse-wave {
  animation: pulse-wave 2s ease-in-out infinite;
  background: linear-gradient(135deg, #4b0082, #000000);
}
</style>
