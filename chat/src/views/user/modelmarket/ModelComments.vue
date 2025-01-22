#src/views/user/modelmarket/ModelComments.vue
<template>
  <div class="mt-8">
    <!-- 评论头部 -->
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-4">
        <h2 class="text-lg font-bold">
          {{ showStats ? "使用统计" : "用户评价" }}
        </h2>
        <el-button type="primary" link @click="showStats = !showStats">
          {{ showStats ? "查看评价" : "查看统计" }}
        </el-button>
      </div>
      <el-button
        v-if="!showStats && userHasPulled && !userReview"
        @click="showReviewDialog = true"
        type="primary"
        plain
      >
        评价模型
      </el-button>
    </div>

    <template v-if="!showStats">
      <!-- 评分过滤器 -->
      <div class="mb-6 overflow-x-auto -mx-4 sm:mx-0">
        <div class="px-4 sm:px-0">
          <el-radio-group
            v-model="filterRating"
            @change="handleFilterChange"
            class="whitespace-nowrap"
          >
            <el-radio-button :value="0">全部</el-radio-button>
            <el-radio-button
              v-for="rating in [5, 4, 3, 2, 1]"
              :key="rating"
              :value="rating"
            >
              {{ rating }}星
            </el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <!-- 评价列表 -->
      <div v-if="reviews.length > 0" class="space-y-6">
        <div
          v-for="review in reviews"
          :key="review.id"
          class="review-item border-b pb-6"
        >
          <div class="flex justify-between items-start mb-3">
            <div class="flex items-center">
              <!-- 评价用户头像 -->
              <div
                class="w-10 h-10 bg-indigo-600 rounded-full mr-3 flex items-center justify-center text-white text-lg overflow-hidden"
              >
                <img
                  v-if="review.avatar"
                  :src="review.avatar"
                  class="w-full h-full object-cover"
                />
                <span v-else>{{
                  review.username.charAt(0).toUpperCase()
                }}</span>
              </div>
              <div>
                <div class="flex items-center">
                  <span class="font-medium">{{ review.username }}</span>
                  <el-tag
                    v-if="review.user_id === modelCreatorId"
                    size="small"
                    type="primary"
                    class="ml-2"
                  >
                    作者
                  </el-tag>
                  <span class="text-gray-500 text-sm ml-2">
                    {{ formatDate(review.created_at) }}
                  </span>
                </div>
                <div class="flex items-center mt-1">
                  <el-rate v-model="review.rating" disabled />
                </div>
              </div>
            </div>
            <div class="flex gap-4">
              <el-button
                v-if="canDeleteReview(review)"
                type="danger"
                link
                @click="handleDeleteReview(review.id)"
              >
                删除
              </el-button>
              <el-button
                type="primary"
                link
                @click="showCommentInput(review.id)"
              >
                回复
              </el-button>
            </div>
          </div>
          <p class="text-gray-700 ml-13">{{ review.comment }}</p>

          <!-- 评论输入框 -->
          <div v-if="activeReviewId === review.id" class="mt-4 ml-13">
            <el-input
              v-model="commentText"
              type="textarea"
              :rows="2"
              placeholder="输入回复内容..."
              maxlength="1000"
              show-word-limit
            />
            <div class="mt-2 flex justify-end gap-2">
              <el-button @click="cancelComment">取消</el-button>
              <el-button type="primary" @click="submitComment(review.id)">
                提交回复
              </el-button>
            </div>
          </div>

          <!-- 评论树 -->
          <div
            v-if="review.comments && review.comments.length > 0"
            class="mt-4 ml-13"
          >
            <CommentTree
              :comments="review.comments"
              :reviewId="review.id"
              :modelCreatorId="modelCreatorId"
              @reload="loadReviews"
            />
          </div>
        </div>
      </div>
      <div v-else class="text-center text-gray-500 py-8">暂无评价</div>

      <!-- 加载更多评价 -->
      <div v-if="hasMoreReviews" class="text-center mt-6">
        <el-button @click="loadMoreReviews" :loading="loadingReviews" plain>
          加载更多
        </el-button>
      </div>
    </template>

    <template v-else>
      <ModelStats :model="modelData" />
    </template>

    <!-- 评价对话框 -->
    <el-dialog v-model="showReviewDialog" title="评价模型" width="92%">
      <el-form :model="reviewForm" ref="reviewFormRef" :rules="reviewRules">
        <el-form-item prop="rating">
          <el-rate v-model="reviewForm.rating" />
        </el-form-item>
        <el-form-item prop="comment">
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            placeholder="请输入你的使用体验..."
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="showReviewDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="submitReview"
            :loading="submittingReview"
          >
            提交评价
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { request } from "@/utils/request";
import { useUserStore } from "@/stores/user";
import CommentTree from "./CommentTree.vue";
import ModelStats from "./ModelStats.vue";

const props = defineProps({
  modelId: {
    type: Number,
    required: true,
  },
  modelCreatorId: {
    type: Number,
    required: true,
  },
  userHasPulled: {
    type: Boolean,
    required: true,
  },
  userReview: {
    type: Object,
    default: null,
  },
  reviewStats: {
    type: Object,
    required: true,
  },
  modelData: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["review-submitted"]);
const userStore = useUserStore();

const reviews = ref([]);
const loadingReviews = ref(false);
const showReviewDialog = ref(false);
const submittingReview = ref(false);
const hasMoreReviews = ref(true);
const currentPage = ref(1);
const filterRating = ref(0);
const activeReviewId = ref(null);
const commentText = ref("");
const showStats = ref(false);

const reviewFormRef = ref(null);
const reviewForm = ref({
  rating: 0,
  comment: "",
});

const reviewRules = {
  rating: [
    { required: true, message: "请选择评分", trigger: "change" },
    { type: "number", min: 1, message: "请至少选择一颗星", trigger: "change" },
  ],
  comment: [
    { required: true, message: "请输入评价内容", trigger: "blur" },
    { min: 10, message: "评价内容至少10个字符", trigger: "blur" },
    { max: 1000, message: "评价内容最多1000个字符", trigger: "blur" },
  ],
};

// 加载评价列表
const loadReviews = async (append = false) => {
  if (loadingReviews.value) return;

  loadingReviews.value = true;
  try {
    const url = new URL(
      `/api/market/models/${props.modelId}/reviews`,
      window.location.origin
    );
    url.searchParams.set("page", currentPage.value);
    url.searchParams.set("page_size", 20);
    if (filterRating.value > 0) {
      url.searchParams.set("rating", filterRating.value);
    }

    const data = await request(url.toString());

    if (append) {
      reviews.value.push(...data.items);
    } else {
      reviews.value = data.items;
    }

    hasMoreReviews.value = data.items.length === 20;
    if (append) {
      currentPage.value++;
    }
  } catch (error) {
    ElMessage.error({
      message: "加载评价失败",
      plain: true,
    });
  } finally {
    loadingReviews.value = false;
  }
};

// 处理评分过滤
const handleFilterChange = () => {
  currentPage.value = 1;
  loadReviews();
};

// 加载更多评价
const loadMoreReviews = () => {
  loadReviews(true);
};

// 删除评价
const handleDeleteReview = async (reviewId) => {
  try {
    await ElMessageBox.confirm("确定要删除这条评价吗？", "确认删除", {
      type: "warning",
    });

    await request(`/api/market/models/${props.modelId}/reviews/${reviewId}`, {
      method: "DELETE",
    });

    ElMessage.success({
      message: "评价已删除",
      plain: true,
    });

    currentPage.value = 1;
    loadReviews();
    emit("review-submitted");
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error({
        message: error.response?.data?.detail || "删除评价失败",
        plain: true,
      });
    }
  }
};

// 评论相关方法
const showCommentInput = (reviewId) => {
  activeReviewId.value = reviewId;
  commentText.value = "";
};

const cancelComment = () => {
  activeReviewId.value = null;
  commentText.value = "";
};

const submitComment = async (reviewId) => {
  if (!commentText.value.trim()) {
    ElMessage.warning({
      message: "请输入回复内容",
      plain: true,
    });
    return;
  }

  try {
    await request(`/api/market/reviews/${reviewId}/comments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content: commentText.value.trim(),
      }),
    });

    ElMessage.success({
      message: "回复提交成功",
      plain: true,
    });
    cancelComment();
    loadReviews();
  } catch (error) {
    ElMessage.error({
      message: error.response?.data?.detail || "回复提交失败",
      plain: true,
    });
  }
};

// 提交评价
const submitReview = async () => {
  if (!reviewFormRef.value) return;

  try {
    await reviewFormRef.value.validate();

    if (!reviewForm.value.rating || reviewForm.value.rating < 1) {
      ElMessage.warning({
        message: "请至少选择一颗星",
        plain: true,
      });
      return;
    }

    submittingReview.value = true;
    await request(`/api/market/models/${props.modelId}/reviews`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(reviewForm.value),
    });

    ElMessage.success({
      message: "评价提交成功",
      plain: true,
    });

    showReviewDialog.value = false;
    reviewForm.value = {
      rating: 0,
      comment: "",
    };

    currentPage.value = 1;
    await loadReviews();
    emit("review-submitted");
  } catch (error) {
    if (error?.message === "validation") return;
    ElMessage.error({
      message: error.response?.data?.detail || "评价提交失败",
      plain: true,
    });
  } finally {
    submittingReview.value = false;
  }
};

// 工具函数
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

const canDeleteReview = (review) => {
  return (
    localStorage.getItem("userRole") === "admin" ||
    (userStore.user && review && review.user_id === userStore.user.id)
  );
};

// 初始加载评价列表
loadReviews();
</script>

<style scoped>
.comment-item {
  border-left: 3px solid var(--el-color-primary);
}

:deep(.el-dialog__body) {
  padding-top: 20px;
}

.ml-13 {
  margin-left: 3.25rem;
}

/* 优化滚动条显示 */
.el-radio-group {
  display: flex;
  padding-bottom: 4px;
}

.el-radio-group::-webkit-scrollbar {
  display: none;
}
</style>
