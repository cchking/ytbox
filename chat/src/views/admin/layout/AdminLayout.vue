<template>
  <div class="flex h-screen bg-gray-50">
    <!-- 左侧固定侧边栏 -->
    <div
      class="fixed top-0 left-0 h-screen flex flex-col bg-white border-r border-gray-100/60 transition-all duration-300 z-20"
      :class="[
        isSidebarOpen ? 'w-64' : 'w-[68px]',
        isMobile ? 'fixed inset-y-0 left-0 z-50' : '',
      ]"
    >
      <!-- 侧边栏头部 -->
      <div
        class="shrink-0 h-16 border-b border-gray-100/60 px-3 flex items-center"
      >
        <div
          v-if="isSidebarOpen"
          class="text-[15px] font-medium ml-2 text-gray-700"
        >
          管理后台
        </div>
        <button
          class="nav-collapse-btn ml-auto p-2 rounded-lg hover:bg-gray-100/80 transition-colors"
          @click="toggleSidebar"
        >
          <PanelLeft
            class="w-5 h-5 text-gray-500 transition-transform duration-300"
            :class="{ 'rotate-180': !isSidebarOpen }"
          />
        </button>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 overflow-y-auto px-2 py-2 space-y-1 nav-menu">
        <RouterLink
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item w-full flex items-center rounded-xl transition-all relative group"
          :class="[
            isCurrentRoute(item.path)
              ? 'bg-blue-50/70 text-blue-600'
              : 'text-gray-600 hover:bg-gray-100/60',
            !isSidebarOpen ? 'justify-center h-10 w-10 mx-auto' : 'px-4 py-2.5',
          ]"
        >
          <div class="flex items-center gap-3">
            <component
              :is="item.icon"
              class="w-[20px] h-[20px]"
              :class="[
                isCurrentRoute(item.path) ? 'text-blue-600' : 'text-gray-500',
              ]"
            />
            <span v-if="isSidebarOpen" class="text-sm whitespace-nowrap">
              {{ item.name }}
            </span>
          </div>

          <!-- 折叠时的提示 -->
          <div
            v-if="!isSidebarOpen"
            class="nav-tooltip invisible opacity-0 absolute left-full pl-2 pointer-events-none group-hover:visible group-hover:opacity-100"
          >
            <div
              class="px-3 py-1.5 rounded-lg bg-gray-800/95 text-xs text-white whitespace-nowrap"
            >
              {{ item.name }}
            </div>
          </div>
        </RouterLink>
      </nav>
    </div>

    <!-- 右侧主内容区域，使用 margin 留出侧边栏空间 -->
    <div
      class="flex-1 flex flex-col transition-all duration-300"
      :style="{
        marginLeft: isSidebarOpen ? '256px' : '68px',
        width: isSidebarOpen ? 'calc(100% - 256px)' : 'calc(100% - 68px)',
      }"
    >
      <!-- 顶部标题栏 -->
      <header
        class="h-16 bg-white shadow-sm flex items-center justify-between px-6 sticky top-0"
      >
        <div class="flex items-center">
          <h1 class="text-xl font-semibold text-gray-800">
            {{ currentRouteTitle }}
          </h1>
        </div>

        <div class="flex items-center space-x-4">
          <span class="text-gray-600 hidden md:block">管理员</span>
          <button
            @click="logout"
            class="px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md flex items-center"
          >
            <LogOut class="w-4 h-4" />
            <span class="ml-2 md:block">退出登录</span>
          </button>
        </div>
      </header>

      <!-- 主内容区域 -->
      <main class="flex-1 overflow-y-auto p-6 bg-gray-50">
        <RouterView v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>

    <!-- 移动端遮罩层 -->
    <div
      v-if="isMobile && isSidebarOpen"
      class="fixed inset-0 bg-black/50 z-40 md:hidden"
      @click="toggleSidebar"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Users,
  Box,
  Settings,
  FileText,
  BarChart,
  Network,
  Radiation,
  MessageSquare,
  LogOut,
  Menu,
  X,
  PanelLeft,
  Ticket,
  Bot,
} from "lucide-vue-next";

const route = useRoute();
const router = useRouter();

// 菜单项配置
const menuItems = [
  {
    name: "用户管理",
    path: "/admin/users",
    icon: Users,
  },
  {
    name: "模型管理",
    path: "/admin/models",
    icon: Box,
  },
  {
    name: "渠道配置",
    path: "/admin/channels",
    icon: Network,
  },
  {
    name: "系统日志",
    path: "/admin/logs",
    icon: FileText,
  },
  {
    name: "AI请求日志",
    path: "/admin/ai-logs",
    icon: BarChart,
  },
  {
    name: "提示词市场",
    path: "/admin/prompts",
    icon: MessageSquare,
  },
  {
    name: "模型市场",
    path: "/admin/marketmodels",
    icon: Bot,
  },
  {
    name: "危险聊天",
    path: "/admin/danger-logs",
    icon: Radiation,
  },
  {
    name: "生成卡密",
    path: "/admin/create-card",
    icon: Ticket,
  },
  {
    name: "系统设置",
    path: "/admin/settings",
    icon: Settings,
  },
];

// 是否是当前路由
const isCurrentRoute = (path) => {
  return route.path.startsWith(path);
};

// 当前路由标题
const currentRouteTitle = computed(() => {
  return route.meta.title || "管理后台";
});

// 响应式状态
const isSidebarOpen = ref(true);
const isMobile = ref(false);

// 检查是否为移动设备的函数
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768;
  if (isMobile.value) {
    isSidebarOpen.value = false;
  } else {
    isSidebarOpen.value = true;
  }
};

// 窗口大小变化监听器
onMounted(() => {
  window.addEventListener("resize", checkMobile);
  checkMobile();
});

onUnmounted(() => {
  window.removeEventListener("resize", checkMobile);
});

// 切换侧边栏函数
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

// 登出
const logout = () => {
  localStorage.clear();
  router.push("/login");
};
</script>

<style scoped>
.nav-menu {
  height: calc(100vh - 128px); /* 调整为正确的高度：屏幕高度减去头部高度 */
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #fff;
}

.nav-menu::-webkit-scrollbar {
  width: 5px;
}

.nav-menu::-webkit-scrollbar-track {
  background: transparent;
}

.nav-menu::-webkit-scrollbar-thumb {
  background: transparent;
  border-radius: 10px;
}

.nav-menu:hover::-webkit-scrollbar-thumb {
  background: #e5e7eb;
}

.nav-tooltip {
  transition: all 0.2s ease-in-out;
  transform-origin: left;
}

/* 导航项样式优化 */
.nav-item {
  transition: all 0.2s ease-in-out;
  position: relative;
}

.nav-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background-color: #3b82f6;
  transition: height 0.2s ease-in-out;
  border-radius: 0 3px 3px 0;
  opacity: 0;
}

.nav-item:hover::before {
  height: 12px;
  opacity: 1;
}

.nav-item.active::before {
  height: 16px;
  opacity: 1;
}

/* 确保选中和悬浮状态背景为纯色 */
.nav-item:hover {
  background-color: rgba(243, 244, 246, 0.8) !important;
}

.nav-item.active,
.nav-item.router-link-active {
  background-color: rgba(239, 246, 255, 0.8) !important;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
