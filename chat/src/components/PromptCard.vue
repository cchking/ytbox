<template>
  <div
    class="group relative overflow-hidden rounded-lg border border-gray-100 bg-white transition-all hover:shadow-xl hover:-translate-y-1"
    :class="{ 'opacity-75': prompt.status === 'delisted' }"
  >
    <div class="relative">
      <!-- 热门标记 -->
      <div
        v-if="prompt.isHot"
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
                class="px-2 py-0.5 rounded-full text-xs font-medium"
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
            class="px-2 py-1 rounded-full text-xs font-medium"
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
                background: `linear-gradient(to right, ${
                  prompt.gradientFrom || '#4F46E5'
                }, ${prompt.gradientTo || '#9333EA'})`,
              }"
            >
              {{ getInitials(prompt.creator_username) }}
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">
                {{ prompt.creator_username }}
              </p>
              <p class="text-xs text-gray-500">
                创建于 {{ formatDate(prompt.created_at) }}
              </p>
            </div>
          </div>
          <div class="text-lg font-bold text-blue-600">
            {{ prompt.price }} 金币
          </div>
        </div>
      </div>

      <!-- 悬浮遮罩 - 仅管理员可见 -->
      <div
        v-if="isAdmin"
        class="absolute inset-0 flex items-center justify-center bg-black/5 opacity-0 transition-opacity group-hover:opacity-100"
      >
        <div
          class="transform space-x-4 scale-90 group-hover:scale-100 transition-transform"
        >
          <button
            @click="$emit('view', prompt)"
            class="rounded-full bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 inline-flex items-center gap-2"
          >
            <Eye class="h-4 w-4" />
            查看详情
          </button>
        </div>
      </div>
    </div>

    <!-- 卡片操作按钮 -->
    <div class="border-t border-gray-100 p-4">
      <div class="flex justify-between items-center">
        <!-- 左侧按钮组 -->
        <div class="flex gap-2">
          <!-- 仅管理员可查看 -->
          <template v-if="isAdmin">
            <button
              @click="$emit('view', prompt)"
              class="text-blue-600 hover:text-blue-700 inline-flex items-center gap-2 text-sm font-medium"
            >
              <Eye class="h-4 w-4" />
              查看
            </button>
          </template>

          <!-- 点赞和踩按钮 - 已购买用户可操作 -->
          <template v-if="prompt.has_purchased">
            <button
              @click="$emit('vote', prompt, 'like')"
              class="inline-flex items-center gap-2 text-sm font-medium"
              :class="
                prompt.has_voted === 'like'
                  ? 'text-blue-600'
                  : 'text-gray-500 hover:text-blue-600'
              "
            >
              <ThumbsUp class="h-4 w-4" />
              <span>{{ prompt.likes }}</span>
            </button>
            <button
              @click="$emit('vote', prompt, 'dislike')"
              class="inline-flex items-center gap-2 text-sm font-medium"
              :class="
                prompt.has_voted === 'dislike'
                  ? 'text-red-600'
                  : 'text-gray-500 hover:text-red-600'
              "
            >
              <ThumbsDown class="h-4 w-4" />
              <span>{{ prompt.dislikes }}</span>
            </button>
          </template>
          <!-- 未购买时只显示数字 -->
          <template v-else>
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
          </template>

          <!-- 购买/使用按钮 -->
          <template v-if="prompt.creator_id !== currentUserId && !isAdmin">
            <button
              v-if="!prompt.has_purchased"
              @click="$emit('purchase', prompt)"
              class="text-green-600 hover:text-green-700 inline-flex items-center gap-2 text-sm font-medium"
            >
              <ShoppingCart class="h-4 w-4" />
              购买
            </button>
            <button
              v-else
              @click="$emit('use', prompt)"
              class="text-blue-600 hover:text-blue-700 inline-flex items-center gap-2 text-sm font-medium"
            >
              <MessageSquare class="h-4 w-4" />
              使用
            </button>
          </template>
        </div>

        <!-- 右侧管理按钮组 - 仅管理员可见 -->
        <div v-if="isAdmin" class="flex gap-2">
          <!-- 待审核状态的操作按钮 -->
          <template v-if="prompt.status === 'pending'">
            <button
              @click="$emit('review', prompt, 'approve')"
              class="text-green-600 hover:text-green-700"
              title="通过"
            >
              <CheckCircle class="h-4 w-4" />
            </button>
            <button
              @click="$emit('review', prompt, 'reject')"
              class="text-red-600 hover:text-red-700"
              title="拒绝"
            >
              <XCircle class="h-4 w-4" />
            </button>
          </template>

          <!-- 已通过状态的操作按钮 -->
          <template v-if="prompt.status === 'approved'">
            <button
              @click="$emit('delist', prompt)"
              class="text-gray-600 hover:text-gray-700"
              title="下架"
            >
              <Archive class="h-4 w-4" />
            </button>
          </template>

          <!-- 已下架状态的操作按钮 -->
          <template v-if="prompt.status === 'delisted'">
            <button
              @click="$emit('list', prompt)"
              class="text-blue-600 hover:text-blue-700"
              title="上架"
            >
              <ArrowUp class="h-4 w-4" />
            </button>
          </template>

          <button
            @click="$emit('manageTags', prompt)"
            class="text-blue-600 hover:text-blue-700"
            title="管理标签"
          >
            <Tags class="h-4 w-4" />
          </button>

          <button
            @click="$emit('delete', prompt)"
            class="text-red-600 hover:text-red-700"
            title="删除"
          >
            <Trash class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ThumbsUp,
  ThumbsDown,
  Eye,
  CheckCircle,
  XCircle,
  Archive,
  ArrowUp,
  Trash,
  Tags,
  ShoppingCart,
  MessageSquare,
} from "lucide-vue-next";

// 定义props
const props = defineProps({
  prompt: {
    type: Object,
    required: true,
  },
  isAdmin: {
    type: Boolean,
    default: false,
  },
  currentUserId: {
    type: [Number, String],
    required: true,
  },
});

// 定义事件
defineEmits([
  "view",
  "review",
  "delist",
  "list",
  "manageTags",
  "delete",
  "vote",
  "purchase",
  "use",
]);

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
const formatDate = (date) => {
  return new Date(date).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
};
</script>
