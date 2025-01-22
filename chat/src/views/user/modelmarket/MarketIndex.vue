<template>
  <div class="market-container p-4 sm:p-6">
    <!-- 顶部区域 -->
    <div
      class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 sm:p-8 rounded-xl mb-4 sm:mb-6"
    >
      <h1 class="text-2xl sm:text-3xl font-bold mb-2">模型市场</h1>
      <p class="text-blue-100 mb-4 text-sm sm:text-base">
        探索、分享和交易高质量的AI模型
      </p>
      <el-button @click="handlePublish" type="primary" plain>
        发布模型
      </el-button>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="bg-white p-4 rounded-lg shadow-sm mb-4 sm:mb-6">
      <div class="flex flex-col sm:flex-row gap-3 sm:gap-4">
        <el-input
          v-model="searchParams.search"
          placeholder="搜索模型"
          class="w-full sm:w-64"
          clearable
          @change="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <div class="flex gap-2 sm:gap-4 overflow-x-auto pb-2 sm:pb-0">
          <el-select
            v-model="searchParams.distribution_type"
            placeholder="分发方式"
            class="w-full sm:w-32"
            clearable
            @change="handleSearch"
          >
            <el-option label="免费拉取" value="free_pull" />
            <el-option label="金币拉取" value="coin_pull" />
            <el-option label="激活码拉取" value="key_pull" />
          </el-select>

          <el-select
            v-model="searchParams.usage_type"
            placeholder="使用方式"
            class="w-full sm:w-32"
            clearable
            @change="handleSearch"
          >
            <el-option label="免费使用" value="free" />
            <el-option label="付费使用" value="coin" />
          </el-select>

          <el-select
            v-model="searchParams.sort_by"
            placeholder="排序方式"
            class="w-full sm:w-32"
            @change="handleSearch"
          >
            <el-option label="最新发布" value="created_at" />
            <el-option label="拉取次数" value="pull_count" />
            <el-option label="使用次数" value="usage_count" />
            <el-option label="评分" value="rating" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 模型列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
      <div
        v-for="model in models"
        :key="model.id"
        class="border rounded-lg p-3 sm:p-4 hover:shadow-lg transition-shadow cursor-pointer"
        @click="showModelDetail(model.id)"
      >
        <div class="flex items-start gap-3 sm:gap-4">
          <!-- 左侧图标 -->
          <img
            :src="model.icon || '/default-model-icon.png'"
            alt="model icon"
            class="w-14 sm:w-16 h-14 sm:h-16 object-cover rounded"
          />

          <!-- 右侧信息 -->
          <div class="flex-1 min-w-0">
            <h3
              class="text-base sm:text-lg font-semibold mb-1 sm:mb-2 truncate"
            >
              {{ model.name }}
            </h3>
            <p class="text-gray-600 text-xs sm:text-sm mb-2 line-clamp-2">
              {{ model.description }}
            </p>

            <div
              class="flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm text-gray-500"
            >
              <span class="whitespace-nowrap">
                {{
                  model.distribution_type === "free_pull"
                    ? "免费拉取"
                    : model.distribution_type === "coin_pull"
                    ? `${model.pull_price}金币拉取`
                    : "激活码拉取"
                }}
              </span>
              <span class="whitespace-nowrap">
                {{
                  model.usage_type === "free"
                    ? "免费使用"
                    : `${model.usage_price}金币/次`
                }}
              </span>
            </div>

            <div
              class="flex flex-wrap items-center justify-between mt-2 text-xs sm:text-sm text-gray-500"
            >
              <div class="flex items-center flex-wrap gap-2">
                <span>评分: {{ model.rating?.toFixed(1) || "--" }}</span>
                <span class="hidden sm:inline">|</span>
                <span>拉取: {{ model.pull_count }}</span>
                <span class="hidden sm:inline">|</span>
                <span>使用: {{ model.usage_count }}</span>
              </div>
              <div class="mt-1 sm:mt-0">
                {{ formatDateTime(model.created_at) }}
              </div>
            </div>

            <!-- 状态标签 -->
            <div class="mt-2">
              <el-tag :type="getStatusType(model.status)" size="small">
                {{ getStatusText(model.status) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > 0" class="flex justify-center mt-4">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="20"
        :total="total"
        :background="true"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 空状态 -->
    <el-empty v-if="total === 0" description="暂无模型" />

    <!-- 模型详情弹窗 -->
    <Teleport to="body">
      <div v-if="showDetail" class="fixed inset-0 bg-black bg-opacity-50 z-40">
        <div
          class="min-h-screen w-full flex items-start sm:items-center justify-center p-0 sm:p-4"
        >
          <div
            class="bg-white w-full sm:max-w-6xl rounded-none sm:rounded-xl h-screen sm:h-auto sm:max-h-[90vh] overflow-y-auto"
          >
            <component
              :is="modelDetailComponent"
              :modelId="selectedModelId"
              @close="closeDetail"
            />
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 发布模型弹窗 -->
    <PublishModelDialog
      v-model="showPublishDialog"
      @published="handlePublished"
    />
  </div>
</template>

<script setup>
import { ref, reactive, defineAsyncComponent, markRaw } from "vue";
import { Search } from "lucide-vue-next";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";
import { useRouter } from "vue-router";
import PublishModelDialog from "./PublishDialog.vue";

const router = useRouter();

// 异步加载模型详情组件
const ModelDetail = defineAsyncComponent(() => import("./ModelDetail.vue"));

// 详情弹窗状态
const showDetail = ref(false);
const selectedModelId = ref(null);
const modelDetailComponent = ref(null);
const showPublishDialog = ref(false);

// 显示详情处理函数
const showModelDetail = (modelId) => {
  selectedModelId.value = Number(modelId);
  modelDetailComponent.value = markRaw(ModelDetail);
  showDetail.value = true;
  document.body.style.overflow = "hidden";
};

// 关闭详情处理函数
const closeDetail = () => {
  showDetail.value = false;
  selectedModelId.value = null;
  modelDetailComponent.value = null;
  document.body.style.overflow = "auto";
};

// 发布处理函数
const handlePublish = () => {
  showPublishDialog.value = true;
};

// 发布成功处理
const handlePublished = () => {
  currentPage.value = 1;
  loadModels();
};

// 添加时间格式化函数
function formatDateTime(dateString) {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// 搜索参数
const searchParams = reactive({
  search: "",
  distribution_type: "",
  usage_type: "",
  sort_by: "created_at",
});

// 列表数据
const models = ref([]);
const total = ref(0);
const currentPage = ref(1);

// 初始加载
loadModels();

// 加载数据
async function loadModels() {
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      ...searchParams,
    });

    const response = await request(`/api/market/models?${params}`);
    models.value = response.data;
    total.value = response.total;
  } catch (error) {
    console.error("加载模型列表失败:", error);
    ElMessage.error("加载模型列表失败");
  }
}

// 搜索处理
function handleSearch() {
  currentPage.value = 1;
  loadModels();
}

// 分页处理
function handlePageChange(page) {
  currentPage.value = page;
  loadModels();
}

// 状态处理
function getStatusType(status) {
  const types = {
    pending: "warning",
    approved: "success",
    rejected: "danger",
    delisted: "info",
  };
  return types[status] || "info";
}

function getStatusText(status) {
  const texts = {
    pending: "待审核",
    approved: "已通过",
    rejected: "已拒绝",
    delisted: "已下架",
  };
  return texts[status] || status;
}
</script>

<style scoped>
.market-container {
  min-height: 100vh;
  background-color: white;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 自定义滚动条样式 */
.modal-content::-webkit-scrollbar {
  width: 4px;
}

.modal-content::-webkit-scrollbar-track {
  background: transparent;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}

@media (max-width: 640px) {
  .el-pagination {
    transform: scale(0.9);
  }
}
</style>
