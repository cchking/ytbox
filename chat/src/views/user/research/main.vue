<template>
  <NavBar title="研究" />
  <div class="h-screen flex bg-gray-50">
    <!-- 侧边栏 -->
    <div
      class="fixed top-0 left-0 h-full bg-white border-r border-gray-200 transition-all duration-300"
      :class="[isCollapsed ? 'w-16' : 'w-64']"
    >
      <!-- 折叠按钮 -->
      <div
        class="h-16 flex items-center justify-end px-3 border-b border-gray-100"
      >
        <button
          @click="toggleCollapse"
          class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <PanelLeft
            class="w-5 h-5 text-gray-500 transition-transform duration-300"
            :class="{ 'rotate-180': isCollapsed }"
          />
        </button>
      </div>

      <!-- 导航菜单 -->
      <nav class="p-2 space-y-2">
        <button
          v-for="item in menuItems"
          :key="item.id"
          @click="setActiveView(item)"
          class="w-full flex items-center rounded-lg transition-all relative group"
          :class="[
            activeView === item.id
              ? 'bg-blue-50 text-blue-600'
              : 'text-gray-600 hover:bg-gray-100',
            isCollapsed ? 'justify-center p-3' : 'px-4 py-3',
          ]"
        >
          <component
            :is="item.icon"
            class="w-5 h-5"
            :class="[
              activeView === item.id ? 'text-blue-600' : 'text-gray-500',
            ]"
          />
          <span v-if="!isCollapsed" class="ml-3 text-sm">
            {{ item.label }}
          </span>

          <!-- 折叠时的工具提示 -->
          <div
            v-if="isCollapsed"
            class="invisible group-hover:visible absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap"
          >
            {{ item.label }}
          </div>
        </button>
      </nav>
    </div>

    <!-- 主要内容区域 -->
    <div
      class="flex-1 transition-all duration-300"
      :class="[isCollapsed ? 'ml-16' : 'ml-64']"
    >
      <Transition name="fade" mode="out-in">
        <component :is="currentComponent"></component>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { PanelLeft, Image, Video } from "lucide-vue-next";
import NavBar from "@/components/NavBar.vue";
import VideoGenerator from "./VideoGenerator.vue";
import ImageGenerator from "./ImageGenerator.vue";

// 响应式状态
const isCollapsed = ref(true);
const activeView = ref("image");

// 使用 computed 来动态返回当前应该显示的组件
const currentComponent = computed(() => {
  return activeView.value === "image" ? ImageGenerator : VideoGenerator;
});

// 菜单配置
const menuItems = [
  {
    id: "image",
    icon: Image,
    label: "图像生成",
  },
  {
    id: "video",
    icon: Video,
    label: "视频生成",
  },
];

// 方法
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

const setActiveView = (item) => {
  activeView.value = item.id;
};
</script>

<style scoped>
/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 确保所有过渡效果平滑 */
* {
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
