<template>
  <header
    class="h-[3.25rem] sm:h-16 px-3 sm:px-6 bg-white border-b border-gray-100 flex items-center justify-between fixed top-0 left-0 right-0 z-50 shadow-sm"
  >
    <!-- 左侧返回按钮 -->
    <button
      class="p-2 -ml-2 rounded-full hover:bg-gray-100 text-gray-700 hover:text-gray-900 transition-colors active:bg-gray-200"
      @click="router.back()"
    >
      <ArrowLeft class="h-5 w-5 sm:h-6 sm:w-6 stroke-2" />
    </button>

    <!-- 中间标题 -->
    <h1
      class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-base sm:text-lg font-medium sm:font-semibold text-gray-900 truncate max-w-[12rem] sm:max-w-xs text-center"
    >
      {{ title }}
    </h1>

    <!-- 右侧用户按钮 -->
    <button
      class="p-2 -mr-2 rounded-full hover:bg-gray-100 text-gray-700 hover:text-gray-900 transition-colors active:bg-gray-200 relative"
      @click="router.push('/console')"
    >
      <LayoutDashboard class="h-5 w-5 sm:h-6 sm:w-6 stroke-2" />
      <!-- 未读消息小红点 -->
      <span
        v-if="hasNotification"
        class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"
      ></span>
    </button>
  </header>

  <!-- 占位元素，防止内容被fixed header遮挡 -->
  <div class="h-[3.25rem] sm:h-16"></div>
</template>

<script setup>
import { ArrowLeft, User, LayoutDashboard } from "lucide-vue-next";
import { useRouter } from "vue-router";

defineProps({
  title: {
    type: String,
    required: true,
  },
  hasNotification: {
    type: Boolean,
    default: false,
  },
});

const router = useRouter();
</script>

<style scoped>
/* 添加按钮激活态样式 */
@media (hover: none) {
  button:active {
    background-color: rgba(0, 0, 0, 0.05);
  }
}
</style>
