<!-- src/components/Sidebar.vue -->
<template>
  <div
    ref="sidebarRef"
    class="fixed top-0 bottom-0 left-0 flex flex-col bg-white shadow-lg z-50 transition-transform duration-300"
    :class="{
      'translate-x-0': isVisible,
      '-translate-x-full': !isVisible,
    }"
    :style="{ width: `${sidebarWidth}px` }"
  >
    <!-- 移动端关闭按钮
    <div
      v-if="props.isMobile"
      class="absolute right-2 top-2 p-2 cursor-pointer"
      @click="isVisible = false"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        class="text-gray-500"
      >
        <path d="M18 6L6 18"></path>
        <path d="M6 6l12 12"></path>
      </svg>
    </div> -->

    <!-- 初始位置指示器 -->
    <div
      class="absolute right-0 top-0 bottom-0 w-px transition-opacity duration-200"
      :class="{
        'opacity-100 border-r border-dashed border-gray-300':
          showInitialIndicator,
        'opacity-0': !showInitialIndicator,
      }"
      :style="{ left: `${props.initialWidth}px` }"
    ></div>

    <!-- 拖动条 -->
    <div
      v-if="!props.isMobile"
      class="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-gray-300 transition-all duration-200"
      :class="{
        'bg-blue-500 shadow-md': isNearInitialPosition,
        'hover:scale-x-150': isResizing,
      }"
      @mousedown="startResize"
      :title="isNearInitialPosition ? '当前接近初始宽度' : '拖动调整宽度'"
    ></div>

    <!-- 内容区域 -->
    <div class="flex-1 flex flex-col h-full overflow-hidden">
      <FolderSection
        @chat-selected="handleChatSelect"
        @create-chat="handleCreateChat"
        @folder-change="handleFolderChange"
        @chat-change="handleChatsChange"
        class="h-2/5"
      />

      <div class="flex-1 overflow-y-auto">
        <ToolSection />
      </div>

      <div class="mt-auto">
        <UserSection :username="username" :userType="userType" />
      </div>

      <div class="w-80">
        <ThemeSection
          :colors="themeColors"
          @change="$emit('themeChange', $event)"
        />
      </div>
    </div>
  </div>

  <!-- 移动端遮罩层 -->
  <div
    v-if="props.isMobile && isVisible"
    class="fixed inset-0 bg-black bg-opacity-50 z-40"
    @click="isVisible = false"
  ></div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import FolderSection from "./FolderSection.vue";
import ToolSection from "./ToolSection.vue";
import UserSection from "./UserSection.vue";
import ThemeSection from "./ThemeSection.vue";

const props = defineProps({
  username: String,
  userType: String,
  themeColors: Array,
  initialWidth: {
    type: Number,
    default: 320,
  },
  isMobile: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "themeChange",
  "widthChange",
  "chat-selected",
  "create-chat",
  "chat-change",
  "folder-change",
]);

// 基础状态
const sidebarRef = ref(null);
const sidebarWidth = ref(props.initialWidth);
const isResizing = ref(false);
const isVisible = ref(!props.isMobile); // 控制显示状态
let startX = 0;
let startWidth = 0;

// 计算属性
const showInitialIndicator = computed(
  () =>
    isResizing.value && Math.abs(sidebarWidth.value - props.initialWidth) < 50
);

const isNearInitialPosition = computed(() => {
  return (
    Math.abs(sidebarWidth.value - props.initialWidth) <= 2 && isResizing.value
  );
});

// 加载保存的宽度
onMounted(() => {
  const savedWidth = localStorage.getItem("sidebarWidth");
  if (savedWidth) {
    sidebarWidth.value = parseInt(savedWidth);
    emit("widthChange", sidebarWidth.value);
  }
});

// 监听宽度变化并保存
watch(sidebarWidth, (newWidth) => {
  localStorage.setItem("sidebarWidth", newWidth.toString());
  emit("widthChange", newWidth);
});

// 事件处理函数
const handleChatSelect = (chat) => {
  emit("chat-selected", chat);
  if (props.isMobile) {
    isVisible.value = false;
  }
};

const handleCreateChat = (chat) => {
  emit("create-chat", chat);
};

const handleFolderChange = (folders) => {
  emit("folder-change", folders);
};

const handleChatsChange = (chats) => {
  emit("chat-change", chats);
};

const startResize = (event) => {
  if (props.isMobile) return;
  isResizing.value = true;
  startX = event.pageX;
  startWidth = sidebarWidth.value;
  document.addEventListener("mousemove", handleResize);
  document.addEventListener("mouseup", stopResize);
  document.body.classList.add("select-none");
};

const handleResize = (event) => {
  if (!isResizing.value) return;
  const diff = event.pageX - startX;
  let newWidth = startWidth + diff;

  // 添加吸附效果：当接近初始宽度时
  const snapThreshold = 10; // 吸附阈值（像素）
  if (Math.abs(newWidth - props.initialWidth) < snapThreshold) {
    newWidth = props.initialWidth;
  }

  // 确保宽度在允许范围内
  const finalWidth = Math.max(240, Math.min(480, newWidth));
  sidebarWidth.value = finalWidth;
};

const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener("mousemove", handleResize);
  document.removeEventListener("mouseup", stopResize);
  document.body.classList.remove("select-none");
};

// 窗口调整大小处理
const handleWindowResize = () => {
  if (sidebarWidth.value > window.innerWidth * 0.8) {
    sidebarWidth.value = Math.max(240, window.innerWidth * 0.8);
    emit("widthChange", sidebarWidth.value);
  }

  // 在窗口调整大小时判断是否需要隐藏侧边栏
  if (window.innerWidth < 768) {
    isVisible.value = false;
  }
};

// 暴露方法给父组件
defineExpose({
  open() {
    isVisible.value = true;
  },
  close() {
    isVisible.value = false;
  },
});

onMounted(() => {
  window.addEventListener("resize", handleWindowResize);
});

onUnmounted(() => {
  document.removeEventListener("mousemove", handleResize);
  document.removeEventListener("mouseup", stopResize);
  window.removeEventListener("resize", handleWindowResize);
});
</script>

<style scoped>
.select-none {
  user-select: none;
}

/* 添加平滑过渡效果 */
.transition-all {
  transition: all 0.2s ease;
}

/* 拖动条悬停效果 */
.hover\:scale-x-150:hover {
  transform: scaleX(1.5);
}

/* 吸附指示器样式 */
.border-dashed {
  border-style: dashed;
}

/* 只对拖动条的颜色变化添加过渡效果 */
.bg-blue-500 {
  background-color: #3b82f6;
  transition: background-color 0.15s ease;
}

/* 阴影效果 */
.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>
