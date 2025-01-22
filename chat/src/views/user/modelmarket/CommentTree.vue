<template>
  <div class="comments-tree">
    <div
      v-for="comment in comments"
      :key="comment.id"
      class="comment-item bg-gray-50/80 p-3 sm:p-4 rounded mb-2"
    >
      <div class="flex justify-between items-start gap-3">
        <!-- 评论者头像 -->
        <div
          class="w-7 h-7 sm:w-8 sm:h-8 rounded-full overflow-hidden bg-gray-200 flex-shrink-0"
        >
          <template v-if="comment.avatar">
            <img
              :src="comment.avatar"
              class="w-full h-full object-cover"
              alt="avatar"
            />
          </template>
          <template v-else>
            <div
              class="w-full h-full flex items-center justify-center bg-blue-100 text-blue-600 text-sm"
            >
              {{ comment.username?.charAt(0).toUpperCase() }}
            </div>
          </template>
        </div>

        <div class="flex-1 min-w-0">
          <!-- 用户信息和操作按钮 -->
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <div class="flex items-center gap-1 flex-wrap">
                <span class="font-medium text-gray-900 text-sm sm:text-base">
                  {{ comment.username }}
                </span>
                <el-tag
                  v-if="comment.user_id === modelCreatorId"
                  size="small"
                  type="primary"
                  class="flex-shrink-0 scale-90 sm:scale-100"
                >
                  作者
                </el-tag>
              </div>
              <p class="text-sm sm:text-base text-gray-700 mt-1 break-words">
                {{ comment.content }}
              </p>
            </div>
          </div>

          <!-- 底部操作栏 -->
          <div
            class="flex flex-wrap items-center gap-x-4 gap-y-2 mt-2 text-xs sm:text-sm"
          >
            <span class="text-gray-500">{{
              formatDate(comment.created_at)
            }}</span>
            <div class="flex items-center gap-3">
              <el-button
                v-if="comment.children?.length > 0"
                type="primary"
                link
                size="small"
                class="text-xs sm:text-sm !p-0"
                @click="toggleChildren(comment.id)"
              >
                {{
                  expandedComments[comment.id]
                    ? "收起回复"
                    : `展开回复(${comment.children.length})`
                }}
              </el-button>
              <el-button
                v-if="canDeleteComment(comment)"
                type="danger"
                link
                size="small"
                class="text-xs sm:text-sm !p-0"
                @click="handleDeleteComment(comment.id)"
              >
                删除
              </el-button>
              <el-button
                type="primary"
                link
                size="small"
                class="text-xs sm:text-sm !p-0"
                @click="showReplyInput(comment)"
              >
                回复
              </el-button>
            </div>
          </div>

          <!-- 回复输入框 -->
          <div v-if="activeCommentId === comment.id" class="mt-3">
            <el-input
              v-model="commentText"
              type="textarea"
              :rows="2"
              placeholder="输入回复内容..."
              maxlength="1000"
              show-word-limit
              resize="none"
              class="bg-white"
            />
            <div class="mt-2 flex justify-end gap-2">
              <el-button size="small" @click="cancelReply">取消</el-button>
              <el-button
                size="small"
                type="primary"
                @click="submitReply(comment)"
              >
                提交回复
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 子评论 -->
      <div
        v-if="comment.children?.length > 0 && expandedComments[comment.id]"
        class="pl-6 sm:pl-11 mt-3"
      >
        <CommentTree
          :comments="comment.children"
          :reviewId="reviewId"
          :modelCreatorId="modelCreatorId"
          @reload="$emit('reload')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "@/stores/user";
import { request } from "@/utils/request";

const props = defineProps({
  comments: {
    type: Array,
    required: true,
  },
  reviewId: {
    type: Number,
    required: true,
  },
  modelCreatorId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["reload"]);
const userStore = useUserStore();

const activeCommentId = ref(null);
const commentText = ref("");

// 添加展开/收起状态管理
const expandedComments = reactive({});

// 初始化展开状态的函数
const initExpandedState = () => {
  props.comments.forEach((comment) => {
    expandedComments[comment.id] = false; // 默认收起
  });
};

// 监听 comments 变化，重新初始化展开状态
watch(
  () => props.comments,
  () => {
    initExpandedState();
  },
  { immediate: true } // 立即执行一次
);

// 添加切换展开/收起的方法
const toggleChildren = (commentId) => {
  expandedComments[commentId] = !expandedComments[commentId];
};

const formatDate = (date) => {
  if (!date) return "";
  const d = new Date(date);
  if (isNaN(d.getTime())) return "";

  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const canDeleteComment = (comment) => {
  return (
    localStorage.getItem("userRole") === "admin" ||
    (userStore.user && comment && comment.user_id === userStore.user.id)
  );
};

const showReplyInput = (comment) => {
  activeCommentId.value = comment.id;
  commentText.value = "";
};

const cancelReply = () => {
  activeCommentId.value = null;
  commentText.value = "";
};

const submitReply = async (comment) => {
  if (!commentText.value.trim()) {
    ElMessage.warning({
      message: "请输入回复内容",
      plain: true,
    });
    return;
  }

  try {
    await request(`/api/market/reviews/${props.reviewId}/comments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content: commentText.value.trim(),
        parent_id: comment.id,
      }),
    });

    ElMessage.success({
      message: "回复提交成功",
      plain: true,
    });
    cancelReply();
    emit("reload");
  } catch (error) {
    ElMessage.error({
      message: error.response?.data?.detail || "回复提交失败",
      plain: true,
    });
  }
};

const handleDeleteComment = async (commentId) => {
  try {
    await ElMessageBox.confirm("确定要删除这条回复吗？", "确认删除", {
      type: "warning",
    });

    await request(`/api/market/comments/${commentId}`, {
      method: "DELETE",
    });

    ElMessage.success({
      message: "回复已删除",
      plain: true,
    });
    emit("reload");
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error({
        message: error.response?.data?.detail || "删除回复失败",
        plain: true,
      });
    }
  }
};
</script>

<style scoped>
.comment-item {
  border-left: 2px solid var(--el-color-primary-light-7);
}

:deep(.el-textarea__wrapper) {
  box-shadow: none !important;
  border: 1px solid #e5e7eb;
}

:deep(.el-textarea__wrapper:hover),
:deep(.el-textarea__wrapper:focus-within) {
  border-color: var(--el-color-primary);
}

.comment-item + .comment-item {
  margin-top: 0.75rem;
}

/* 优化嵌套评论在移动端的显示 */
@media (max-width: 640px) {
  .comments-tree .comments-tree {
    margin-left: -0.5rem;
  }
}
</style>
