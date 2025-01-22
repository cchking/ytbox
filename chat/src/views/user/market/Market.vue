<template>
  <div class="container mx-auto px-4 py-8">
    <!-- 顶部搜索和筛选区域 -->
    <div class="mb-8 space-y-4">
      <!-- 标题和操作区 -->
      <div
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <h1 class="text-2xl font-bold">提示市场</h1>
        <div
          class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4"
        >
          <!-- 搜索框 -->
          <div class="relative flex-1 sm:flex-none">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索提示..."
              class="w-full sm:w-auto pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              @input="handleSearch"
            />
            <Search class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          </div>

          <!-- 排序下拉菜单 -->
          <select
            v-model="sortBy"
            class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="handleSort"
          >
            <option value="newest">最新</option>
            <option value="popular">最热门</option>
            <option value="price-asc">价格从低到高</option>
            <option value="price-desc">价格从高到低</option>
          </select>

          <!-- 发布按钮 -->
          <button
            @click="showCreateDialog"
            class="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
          >
            <Plus class="w-5 h-5" />
            <span>发布提示词</span>
          </button>
        </div>
      </div>

      <!-- 标签筛选 移动端支持横向滚动 -->
      <div
        class="overflow-x-auto pb-2 -mx-4 px-4 sm:overflow-visible sm:pb-0 sm:mx-0 sm:px-0"
      >
        <div class="flex flex-nowrap sm:flex-wrap gap-2 min-w-min">
          <button
            v-for="tag in tags"
            :key="tag.id"
            class="shrink-0 px-3 py-1 rounded-full text-sm font-medium transition-colors"
            :class="
              selectedTags.includes(tag.id)
                ? 'bg-blue-100 text-blue-700 border border-blue-200'
                : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
            "
            @click="toggleTag(tag.id)"
          >
            {{ tag.name }}
          </button>
        </div>
      </div>
    </div>

    <!-- 提示列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
      <template v-if="!loading">
        <PromptCard
          v-for="prompt in filteredPrompts"
          :key="prompt.id"
          :prompt="prompt"
          :is-admin="isAdmin"
          :current-user-id="currentUserId"
          @view="handleView"
          @purchase="handlePurchase"
          @use="handleUse"
          @vote="handleVote"
        />
      </template>
      <template v-else>
        <div
          v-for="n in 6"
          :key="n"
          class="h-48 sm:h-96 rounded-lg bg-gray-100 animate-pulse"
        ></div>
      </template>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore && !loading" class="mt-8 text-center">
      <button
        @click="loadMore"
        class="w-full sm:w-auto px-6 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        加载更多
      </button>
    </div>

    <!-- 空状态 -->
    <div
      v-if="!loading && filteredPrompts.length === 0"
      class="mt-8 text-center text-gray-500"
    >
      暂无相关提示
    </div>

    <!-- 购买确认对话框 -->
    <el-dialog
      v-model="purchaseDialogVisible"
      title="购买提示"
      :width="isMobile ? '90%' : '400px'"
      class="sm:!max-w-md"
    >
      <div class="py-4">
        <p>确认购买 "{{ selectedPrompt?.title }}" ?</p>
        <p class="mt-2 text-gray-600">价格: {{ selectedPrompt?.price }} 金币</p>
      </div>
      <template #footer>
        <div class="flex justify-end gap-4">
          <el-button @click="purchaseDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="purchasing"
            @click="confirmPurchase"
          >
            确认购买
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 发布提示词对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="发布提示词"
      :width="isMobile ? '90%' : '600px'"
      :close-on-click-modal="false"
      class="sm:!max-w-2xl"
    >
      <CreatePromptForm
        v-if="createDialogVisible"
        :submitting="submitting"
        @submit="handleCreateSubmit"
        @cancel="createDialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { Search, Plus } from "lucide-vue-next";
import { ElMessage, ElDialog, ElButton } from "element-plus";
import { request } from "@/utils/request";
import PromptCard from "@/components/PromptCard.vue";
import NavBar from "@/components/NavBar.vue";
import CreatePromptForm from "./CreatePromptForm.vue";

export default {
  name: "PromptMarket",
  components: {
    Search,
    Plus,
    ElDialog,
    ElButton,
    PromptCard,
    NavBar,
    CreatePromptForm,
  },

  setup() {
    // 状态变量
    const loading = ref(false);
    const purchasing = ref(false);
    const submitting = ref(false);
    const prompts = ref([]);
    const searchQuery = ref("");
    const sortBy = ref("newest");
    const selectedTags = ref([]);
    const currentPage = ref(1);
    const hasMore = ref(true);
    const purchaseDialogVisible = ref(false);
    const createDialogVisible = ref(false);
    const selectedPrompt = ref(null);
    const currentUserId = ref(null);
    const isAdmin = ref(false);
    const isMobile = ref(window.innerWidth < 640);
    const tags = ref([]);

    // 计算属性：过滤和排序后的提示列表
    const filteredPrompts = computed(() => {
      let result = [...prompts.value];

      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(
          (prompt) =>
            prompt.title.toLowerCase().includes(query) ||
            prompt.description.toLowerCase().includes(query)
        );
      }

      // 标签过滤
      if (selectedTags.value.length > 0) {
        result = result.filter((prompt) =>
          prompt.tags.some((tag) => selectedTags.value.includes(tag.id))
        );
      }

      // 排序
      switch (sortBy.value) {
        case "popular":
          result.sort((a, b) => b.likes - a.likes);
          break;
        case "price-asc":
          result.sort((a, b) => a.price - b.price);
          break;
        case "price-desc":
          result.sort((a, b) => b.price - a.price);
          break;
        default: // newest
          result.sort(
            (a, b) => new Date(b.created_at) - new Date(a.created_at)
          );
      }

      return result;
    });

    // 获取标签列表
    const fetchTags = async () => {
      try {
        const response = await request("/api/admin/tags");
        tags.value = response;
      } catch (error) {
        ElMessage.error({
          message: "获取标签列表失败",
          plain: true,
        });
      }
    };

    // 获取提示列表
    const fetchPrompts = async () => {
      try {
        loading.value = true;
        const response = await request(
          `/api/prompts?page=${currentPage.value}`
        );

        if (currentPage.value === 1) {
          prompts.value = response.data;
        } else {
          prompts.value = [...prompts.value, ...response.data];
        }

        hasMore.value = response.has_more;
      } catch (error) {
        ElMessage.error({
          message: "获取提示列表失败",
          plain: true,
        });
      } finally {
        loading.value = false;
      }
    };

    // 处理页码变化
    const loadMore = () => {
      currentPage.value++;
      fetchPrompts();
    };

    // 处理搜索
    const handleSearch = () => {
      currentPage.value = 1;
      fetchPrompts();
    };

    // 处理排序
    const handleSort = () => {
      currentPage.value = 1;
      fetchPrompts();
    };

    // 处理标签选择
    const toggleTag = (tagId) => {
      const index = selectedTags.value.indexOf(tagId);
      if (index === -1) {
        selectedTags.value.push(tagId);
      } else {
        selectedTags.value.splice(index, 1);
      }
      currentPage.value = 1;
      fetchPrompts();
    };

    // 处理创建提示词
    const showCreateDialog = () => {
      createDialogVisible.value = true;
    };

    const handleCreateSubmit = async (formData) => {
      if (submitting.value) return;

      try {
        submitting.value = true;
        await request("/api/prompt-market/products", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });

        ElMessage.success({
          message: "提示词提交成功，等待审核",
          plain: true,
        });
        createDialogVisible.value = false;

        // 重新加载列表
        currentPage.value = 1;
        await fetchPrompts();
      } catch (error) {
        const errorMsg = error.response?.data?.detail || "发布失败，请重试";
        ElMessage.error({
          message: errorMsg,
          plain: true,
        });
      } finally {
        submitting.value = false;
      }
    };

    // 处理查看、购买、使用
    const handleView = (prompt) => {
      // 处理查看详情
    };

    const handlePurchase = (prompt) => {
      selectedPrompt.value = prompt;
      purchaseDialogVisible.value = true;
    };

    const confirmPurchase = async () => {
      if (!selectedPrompt.value) return;

      try {
        purchasing.value = true;
        await request(
          `/api/prompt-market/products/${selectedPrompt.value.id}/purchase`,
          {
            method: "POST",
          }
        );

        ElMessage.success({
          message: "购买成功",
          plain: true,
        });
        purchaseDialogVisible.value = false;

        // 重新获取提示列表以更新状态
        currentPage.value = 1;
        fetchPrompts();
      } catch (error) {
        if (error.response?.status === 400) {
          ElMessage.warning({
            message: "金币不足",
            plain: true,
          });
        } else {
          ElMessage.error({
            message: "购买失败，请重试",
            plain: true,
          });
        }
      } finally {
        purchasing.value = false;
      }
    };

    const handleUse = (prompt) => {
      // 跳转到使用页面
      window.location.href = `/chat?prompt_id=${prompt.id}`;
    };

    // 处理投票
    const handleVote = async (prompt, vote_type) => {
      try {
        const response = await request(
          `/api/prompt-market/products/${prompt.id}/vote`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ vote_type }),
          }
        );

        // 更新本地状态
        const { likes, dislikes } = response;
        const index = prompts.value.findIndex((p) => p.id === prompt.id);
        if (index !== -1) {
          const updatedPrompt = { ...prompts.value[index] };
          updatedPrompt.likes = likes;
          updatedPrompt.dislikes = dislikes;

          // 更新投票状态
          if (updatedPrompt.has_voted === vote_type) {
            updatedPrompt.has_voted = null;
            ElMessage.success({
              message: `取消${vote_type === "like" ? "点赞" : "踩"}成功`,
              plain: true,
            });
          } else {
            updatedPrompt.has_voted = vote_type;
            ElMessage.success({
              message: `${vote_type === "like" ? "点赞" : "踩"}成功`,
              plain: true,
            });
          }

          prompts.value[index] = updatedPrompt;
        }
      } catch (error) {
        if (error.response?.status === 403) {
          ElMessage.warning({
            message: "请先购买此提示词后再进行投票",
            plain: true,
          });
        } else if (
          error.response?.status === 400 &&
          error.response.data?.detail === "Cannot vote on your own product"
        ) {
          ElMessage.warning({
            message: "不能对自己的提示词进行投票",
            plain: true,
          });
        } else {
          ElMessage.error({
            message: error.response?.data?.detail || "操作失败，请重试",
            plain: true,
          });
        }
      }
    };

    // 处理移动端检测
    const handleResize = () => {
      isMobile.value = window.innerWidth < 640;
    };

    onMounted(async () => {
      // 获取用户信息
      try {
        const userInfo = await request("/api/users/me");
        currentUserId.value = userInfo.id;
        isAdmin.value = userInfo.role === "admin";
      } catch (error) {
        // 处理错误
      }

      // 添加窗口大小监听
      window.addEventListener("resize", handleResize);

      // 获取标签列表
      await fetchTags();

      // 获取提示列表
      fetchPrompts();
    });

    onUnmounted(() => {
      window.removeEventListener("resize", handleResize);
    });

    return {
      // 状态
      loading,
      purchasing,
      submitting,
      prompts,
      searchQuery,
      sortBy,
      selectedTags,
      currentPage,
      hasMore,
      purchaseDialogVisible,
      createDialogVisible,
      selectedPrompt,
      currentUserId,
      isAdmin,
      isMobile,
      tags,
      filteredPrompts,

      // 方法
      loadMore,
      handleSearch,
      handleSort,
      toggleTag,
      showCreateDialog,
      handleCreateSubmit,
      handleView,
      handlePurchase,
      confirmPurchase,
      handleUse,
      handleVote,
    };
  },
};
</script>

<style scoped>
/* 隐藏移动端滚动条但保持可滚动 */
@media (max-width: 640px) {
  .overflow-x-auto {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .overflow-x-auto::-webkit-scrollbar {
    display: none;
  }
}

/* Element Plus 对话框移动端适配 */
:deep(.el-dialog) {
  @apply !rounded-xl;
}

:deep(.el-dialog__header) {
  @apply !px-4 !pt-4 !pb-3 !mb-0 !border-b !border-gray-100;
}

:deep(.el-dialog__body) {
  @apply !p-4;
}

:deep(.el-dialog__footer) {
  @apply !px-4 !py-3 !mt-0 !border-t !border-gray-100;
}

/* 适配移动端触摸操作 */
@media (hover: none) {
  .hover\:bg-blue-600:active {
    @apply bg-blue-600;
  }

  .hover\:bg-gray-200:active {
    @apply bg-gray-200;
  }
}

/* 移动端优化 */
@media (max-width: 640px) {
  .container {
    @apply px-4;
  }

  .el-button {
    @apply text-sm py-2;
  }

  .el-dialog__title {
    @apply text-lg;
  }

  /* 标签滚动阴影提示 */
  .overflow-x-auto {
    background: linear-gradient(to right, white 30%, rgba(255, 255, 255, 0)),
      linear-gradient(to right, rgba(255, 255, 255, 0), white 70%) 100% 0,
      radial-gradient(farthest-side at 0 50%, rgba(0, 0, 0, 0.2), transparent),
      radial-gradient(
          farthest-side at 100% 50%,
          rgba(0, 0, 0, 0.2),
          transparent
        )
        100% 0;
    background-repeat: no-repeat;
    background-size: 40px 100%, 40px 100%, 14px 100%, 14px 100%;
    background-attachment: local, local, scroll, scroll;
  }
}
</style>
