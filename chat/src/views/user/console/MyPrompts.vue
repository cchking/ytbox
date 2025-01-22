# MyPrompts.vue
<template>
  <div class="container mx-auto p-4">
    <!-- 标题和过滤器 -->
    <div
      class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-4 sm:gap-0"
    >
      <h2 class="text-2xl font-bold">我的提示词</h2>
      <!-- 过滤器在移动端改为垂直排列 -->
      <div class="flex flex-col sm:flex-row gap-3 sm:gap-4">
        <!-- 类型过滤器 -->
        <select
          v-model="filters.type"
          class="px-4 py-2 border rounded-lg w-full sm:w-auto"
          @change="handleFiltersChange"
          :disabled="loading"
        >
          <option value="all">全部</option>
          <option value="created">我的发布</option>
          <option value="purchased">我的购买</option>
        </select>
        <!-- 状态过滤器 -->
        <select
          v-model="filters.status"
          class="px-4 py-2 border rounded-lg w-full sm:w-auto"
          @change="handleFiltersChange"
          :disabled="loading"
        >
          <option value="">全部状态</option>
          <option value="pending">待审核</option>
          <option value="approved">已通过</option>
          <option value="rejected">已拒绝</option>
          <option value="delisted">已下架</option>
        </select>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
      {{ error }}
      <button class="ml-2 underline" @click="retryLoad">重试</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div
        class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"
      ></div>
    </div>

    <!-- 空状态 -->
    <div
      v-else-if="prompts.length === 0"
      class="flex flex-col items-center justify-center min-h-[400px] text-gray-500"
    >
      <InboxIcon class="w-12 h-12 mb-4 stroke-1" />
      <p>暂无数据</p>
    </div>

    <!-- 商品列表 -->
    <div
      v-else
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6"
    >
      <div
        v-for="prompt in prompts"
        :key="prompt.id"
        class="group relative overflow-hidden rounded-lg border border-gray-100 bg-white transition-all hover:shadow-xl hover:-translate-y-1"
        :class="{ 'opacity-75': prompt.status === 'delisted' }"
      >
        <div class="relative">
          <!-- 热门标记 -->
          <div
            v-if="prompt.is_hot"
            class="absolute -right-12 top-6 rotate-45 bg-gradient-to-r from-blue-500 to-blue-600 px-10 py-1 text-white"
          >
            <span class="text-xs font-semibold">热门</span>
          </div>

          <!-- 卡片内容 -->
          <div class="p-6">
            <div class="flex items-start justify-between">
              <div>
                <div class="flex flex-wrap gap-2 mb-2">
                  <span
                    v-for="tag in prompt.tags"
                    :key="tag.id"
                    class="shrink-0 px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap"
                    :style="{
                      backgroundColor: `${tag.color}20`,
                      color: tag.color,
                      border: `1px solid ${tag.color}`,
                    }"
                  >
                    {{ tag.name }}
                  </span>
                </div>
                <h3 class="text-xl font-bold text-gray-900 line-clamp-1">
                  {{ prompt.title }}
                </h3>
              </div>
              <span
                class="shrink-0 px-2 py-1 rounded-full text-xs font-medium"
                :class="getStatusClass(prompt.status)"
              >
                {{ getStatusText(prompt.status) }}
              </span>
            </div>

            <p class="mt-4 text-sm text-gray-600 line-clamp-2">
              {{ prompt.description }}
            </p>
          </div>

          <!-- 底部信息 -->
          <div class="border-t border-gray-100 p-6">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="h-10 w-10 overflow-hidden rounded-full flex items-center justify-center text-white font-bold"
                  :style="{
                    background: 'linear-gradient(to right, #4F46E5, #9333EA)',
                  }"
                >
                  {{
                    getInitials(
                      prompt.type === "purchased"
                        ? prompt.creator_username
                        : "我"
                    )
                  }}
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900 line-clamp-1">
                    {{
                      prompt.type === "purchased"
                        ? prompt.creator_username
                        : "我"
                    }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ prompt.type === "purchased" ? "购买于" : "创建于" }}
                    {{
                      formatDate(
                        prompt.type === "purchased"
                          ? prompt.purchase_info?.created_at
                          : prompt.created_at
                      )
                    }}
                  </p>
                </div>
              </div>
              <div class="text-lg font-bold text-blue-600">
                {{ prompt.price }} 金币
              </div>
            </div>
          </div>
        </div>

        <!-- 卡片操作按钮 -->
        <div class="border-t border-gray-100 p-4">
          <div class="flex justify-between items-center">
            <div class="flex gap-2">
              <!-- 点赞和踩统计 -->
              <div
                class="inline-flex items-center gap-2 text-sm font-medium text-gray-500"
              >
                <ThumbsUp class="h-4 w-4" />
                <span>{{ prompt.likes }}</span>
              </div>
              <div
                class="inline-flex items-center gap-2 text-sm font-medium text-gray-500"
              >
                <ThumbsDown class="h-4 w-4" />
                <span>{{ prompt.dislikes }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="prompts.length > 0" class="mt-6 flex justify-center">
      <div class="flex flex-col sm:flex-row items-center gap-4 sm:gap-2">
        <button
          class="w-full sm:w-auto px-4 py-2 border rounded-lg disabled:opacity-50"
          :disabled="currentPage === 1 || loading"
          @click="changePage(currentPage - 1)"
        >
          上一页
        </button>
        <span class="px-4 py-2">第 {{ currentPage }} 页</span>
        <button
          class="w-full sm:w-auto px-4 py-2 border rounded-lg disabled:opacity-50"
          :disabled="!hasMore || loading"
          @click="changePage(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { request } from "@/utils/request";
import { ThumbsUp, ThumbsDown, Inbox as InboxIcon } from "lucide-vue-next";

// 状态
const prompts = ref([]);
const currentPage = ref(1);
const pageSize = 12;
const hasMore = ref(false);
const loading = ref(false);
const error = ref(null);
const filters = ref({
  type: "all",
  status: "",
});

// 获取状态对应的样式
const getStatusClass = (status) => {
  const statusClasses = {
    pending: "bg-yellow-50 text-yellow-700 border border-yellow-200",
    approved: "bg-green-50 text-green-700 border border-green-200",
    rejected: "bg-red-50 text-red-700 border border-red-200",
    delisted: "bg-gray-50 text-gray-700 border border-gray-200",
  };
  return statusClasses[status] || "";
};

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    pending: "待审核",
    approved: "已通过",
    rejected: "已拒绝",
    delisted: "已下架",
  };
  return statusMap[status] || status;
};

// 获取头像缩写
const getInitials = (name) => {
  return name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return "暂无日期";

  try {
    const date = new Date(dateString);

    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      console.warn("Invalid date:", dateString);
      return "日期格式错误";
    }

    // 使用 Intl.DateTimeFormat 进行本地化格式化
    return new Intl.DateTimeFormat("zh-CN", {
      year: "numeric",
      month: "long",
      day: "numeric",
    }).format(date);
  } catch (error) {
    console.error("Error formatting date:", error);
    return "日期处理错误";
  }
};

// 加载提示词数据
const loadPrompts = async () => {
  loading.value = true;
  error.value = null;

  try {
    // 构建查询参数
    const params = new URLSearchParams({
      type: filters.value.type,
      skip: ((currentPage.value - 1) * pageSize).toString(),
      limit: pageSize.toString(),
    });

    // 仅在选择了状态时添加状态参数
    if (filters.value.status) {
      params.append("status", filters.value.status);
    }

    // 发送请求
    const data = await request(`/api/prompt-market/my-prompts?${params}`);

    prompts.value = data.items;
    hasMore.value = data.total > currentPage.value * pageSize;
  } catch (err) {
    console.error("Failed to load prompts:", err);
    error.value = "加载数据失败，请稍后重试";
  } finally {
    loading.value = false;
  }
};

// 重试加载
const retryLoad = () => {
  error.value = null;
  loadPrompts();
};

// 过滤器变化处理
const handleFiltersChange = () => {
  currentPage.value = 1; // 重置页码
  loadPrompts();
};

// 页面切换
const changePage = (page) => {
  currentPage.value = page;
  loadPrompts();
};

// 组件挂载时加载数据
onMounted(() => {
  loadPrompts();
});
</script>

<style scoped>
/* 移动端优化 */
@media (max-width: 640px) {
  .container {
    @apply px-4;
  }

  /* 标签横向滚动优化 */
  .flex-wrap {
    flex-wrap: nowrap;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scroll-padding: 1rem;
    scroll-snap-type: x proximity;
  }

  .flex-wrap::-webkit-scrollbar {
    display: none;
  }
}

/* 触摸设备交互优化 */
@media (hover: none) {
  .hover\:shadow-xl:active {
    @apply shadow-xl;
  }

  .hover\:-translate-y-1:active {
    @apply -translate-y-1;
  }
}
</style>
