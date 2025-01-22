<template>
  <NavBar title="控制台" />
  <div class="flex h-screen">
    <!-- 固定侧边栏 -->
    <div
      class="side-nav fixed top-0 left-0 h-screen flex flex-col bg-gradient-to-b from-white to-gray-50/30 border-r border-gray-100/60"
      :class="[isCollapsed ? 'w-[68px]' : 'w-64']"
    >
      <!-- 顶部区域 -->
      <div
        class="shrink-0 h-16 mt-16 border-b border-gray-100/60 px-3 flex items-center"
      >
        <div
          v-if="!isCollapsed"
          class="text-[15px] font-medium ml-2 text-gray-700"
        >
          控制台
        </div>
        <button
          class="nav-collapse-btn ml-auto p-2 rounded-lg hover:bg-gray-100/80 transition-colors"
          @click="toggleCollapse"
        >
          <PanelLeft
            class="w-5 h-5 text-gray-500 transition-transform duration-300"
            :class="{ 'rotate-180': isCollapsed }"
          />
        </button>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 overflow-y-auto px-2 py-2 space-y-1 nav-menu">
        <template v-for="(item, index) in menuItems" :key="item.id">
          <!-- 分组标题 -->
          <div
            v-if="item.type === 'group'"
            :class="[
              'px-4 py-2 text-xs font-medium text-gray-400 select-none',
              !isCollapsed ? 'text-left' : 'text-center',
            ]"
          >
            {{ !isCollapsed ? item.label : "⋯" }}
          </div>

          <!-- 菜单项 -->
          <button
            v-else
            class="nav-item w-full flex items-center rounded-xl transition-all relative group"
            :class="[
              activeItem === item.id
                ? 'bg-blue-50/70 text-blue-600'
                : 'text-gray-600 hover:bg-gray-100/60',
              isCollapsed ? 'justify-center h-10 w-10 mx-auto' : 'px-4 py-2.5',
              { 'mt-4': index === 3 },
            ]"
            @click="setActiveItem(item)"
          >
            <div class="flex items-center gap-3">
              <component
                :is="item.icon"
                class="w-[20px] h-[20px]"
                :class="[
                  activeItem === item.id ? 'text-blue-600' : 'text-gray-500',
                  item.id === 'vip' && 'text-amber-500',
                ]"
              />
              <span
                v-if="!isCollapsed"
                class="text-sm whitespace-nowrap"
                :class="[item.id === 'vip' && 'text-amber-500']"
              >
                {{ item.label }}
              </span>
            </div>

            <!-- Badge -->
            <div
              v-if="item.badge && !isCollapsed"
              class="ml-auto px-1.5 py-0.5 text-[11px] font-medium rounded-full"
              :class="[
                item.badge.type === 'new' && 'bg-blue-100 text-blue-600',
                item.badge.type === 'hot' && 'bg-rose-100 text-rose-600',
              ]"
            >
              {{ item.badge.text }}
            </div>

            <!-- 折叠时的提示 -->
            <div
              v-if="isCollapsed"
              class="nav-tooltip invisible opacity-0 absolute left-full pl-2 pointer-events-none group-hover:visible group-hover:opacity-100"
            >
              <div
                class="px-3 py-1.5 rounded-lg bg-gray-800/95 text-xs text-white whitespace-nowrap"
              >
                {{ item.label }}
                <span
                  v-if="item.badge"
                  class="ml-1 px-1 py-0.5 rounded text-[10px] bg-white/20"
                >
                  {{ item.badge.text }}
                </span>
              </div>
            </div>
          </button>
        </template>
      </nav>
    </div>

    <!-- 内容区域 -->
    <div
      class="flex-1 p-6 transition-all duration-300"
      :class="[isCollapsed ? 'ml-[68px]' : 'ml-64']"
    >
      <Transition name="fade" mode="out-in">
        <div v-if="currentView" class="h-full">
          <component :is="currentView"></component>
        </div>
        <div
          v-else
          class="flex items-center justify-center h-full text-gray-500"
        >
          请选择一个菜单项
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, markRaw, onMounted, onUnmounted } from "vue";
import NavBar from "@/components/NavBar.vue";
import {
  MessageSquare,
  Sparkles,
  BookOpen,
  History,
  Crown,
  Bot,
  Share,
  PanelLeft,
  ScrollText,
  Star,
  LayoutDashboard,
  ActivitySquare,
  Bookmark,
  Box,
  Lock,
} from "lucide-vue-next";

// 导入视图组件
import DashboardView from "./CoinsLogs.vue";
import PromptsView from "../market/Market.vue";
import PrivatePromptsView from "./PrivatePrompts.vue";
import MyPromptsView from "./MyPrompts.vue";
import HistoryView from "./AiUseLog.vue";
import ShareView from "./InviteShare.vue";
import VipView from "./VIPBenefits.vue";
import GuideView from "./UserGuide.vue";
import ModelHealth from "./ModelHealth.vue";
import modelmarket from "../modelmarket/MarketIndex.vue";
import PublishedModelsManager from "../modelmarket/PublishedModelsManager.vue";
import privatemodels from "../privatemodels/PrivateModels.vue";
// 新增响应式判断函数
const isMobile = () => window.innerWidth <= 768;

// 响应式状态
const isCollapsed = ref(isMobile());
const activeItem = ref("explore");
const currentView = ref(null);

// 用户信息
const user = {
  name: "Alex Chen",
  plan: "高级会员",
};

// 视图组件映射
const viewComponents = {
  DashboardView: markRaw(DashboardView),
  PromptsView: markRaw(PromptsView),
  PrivatePromptsView: markRaw(PrivatePromptsView),
  MyPromptsView: markRaw(MyPromptsView),
  HistoryView: markRaw(HistoryView),
  ShareView: markRaw(ShareView),
  VipView: markRaw(VipView),
  GuideView: markRaw(GuideView),
  ModelHealth: markRaw(ModelHealth),
  modelmarket: markRaw(modelmarket),
  PublishedModelsManager: markRaw(PublishedModelsManager),
  privatemodels: markRaw(privatemodels),
};

// 菜单配置
const menuItems = [
  {
    id: "explore",
    icon: LayoutDashboard,
    label: "控制台",
    view: "DashboardView",
  },
  {
    id: "prompts",
    icon: Sparkles,
    label: "提示词市场",
    badge: { type: "hot", text: "HOT" },
    view: "PromptsView",
  },
  {
    id: "modelmarket",
    icon: Bot,
    label: "模型市场",
    badge: { type: "new", text: "NEW" },
    view: "modelmarket",
  },

  { type: "group", label: "我的空间" },
  {
    id: "my-prompts",
    icon: ScrollText,
    label: "我的prompt",
    view: "MyPromptsView",
  },
  {
    id: "my-prompts",
    icon: ScrollText,
    view: "MyPromptsView",
    id: "starred",
    icon: Bookmark,
    label: "私人prompt",
    view: "PrivatePromptsView",
  },
  {
    id: "PublishedModelsManager",
    icon: Box,
    label: "我的模型",
    view: "PublishedModelsManager",
  },
  {
    id: "privatemodels",
    icon: Lock,
    label: "私人模型",
    view: "privatemodels",
  },
  {
    id: "history",
    icon: History,
    label: "模型日志",
    view: "HistoryView",
  },
  {
    id: "share",
    icon: Share,
    label: "分享中心",
    view: "ShareView",
  },
  { type: "group", label: "权益" },
  {
    id: "vip",
    icon: Crown,
    label: "会员权益",
    view: "VipView",
  },
  {
    id: "guide",
    icon: BookOpen,
    label: "使用指南",
    view: "GuideView",
  },
  {
    id: "health",
    icon: ActivitySquare,
    label: "模型状态",
    view: "ModelHealth",
  },
];

// 方法
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

const setActiveItem = (item) => {
  if (item.view) {
    activeItem.value = item.id;
    currentView.value = viewComponents[item.view];
  }
};

// 监听窗口大小变化
onMounted(() => {
  const handleResize = () => {
    if (isMobile() && !isCollapsed.value) {
      isCollapsed.value = true;
    }
  };

  window.addEventListener("resize", handleResize);

  // 组件卸载时移除监听
  onUnmounted(() => {
    window.removeEventListener("resize", handleResize);
  });
});

// 初始化默认视图
setActiveItem(menuItems[0]);
</script>

<style scoped>
.side-nav {
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
}

.nav-menu {
  height: calc(100vh - 80px);
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

/* 内容过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 确保动画平滑 */
* {
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
