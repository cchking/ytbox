<template>
  <div class="market-models-review">
    <!-- 顶部操作栏 -->
    <div class="header-section mb-6">
      <el-row :gutter="20" class="mb-4">
        <el-col :xs="24" :sm="12" :md="8" class="mb-4 sm:mb-0">
          <h2 class="text-xl sm:text-2xl font-bold">模型市场审核</h2>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-select
            v-model="status"
            placeholder="选择状态"
            @change="loadModels"
            class="w-full"
          >
            <el-option label="全部状态" value="" />
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已下架" value="delisted" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 模型列表 -->
    <div class="model-list-section">
      <!-- 桌面端表格视图 -->
      <div class="hidden md:block">
        <el-table
          :data="models"
          style="width: 100%"
          border
          v-loading="loading"
          class="rounded-xl shadow-sm"
        >
          <el-table-column label="名称" min-width="200">
            <template #default="{ row }">
              <div class="flex items-center">
                <el-image
                  v-if="row.icon"
                  :src="row.icon"
                  class="w-8 h-8 mr-2 rounded"
                  :preview-src-list="[row.icon]"
                />
                <div>
                  <div class="font-medium">{{ row.name }}</div>
                  <div class="text-gray-500 text-sm truncate max-w-md">
                    {{ row.description }}
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="creator_username" label="创建者" width="120" />

          <el-table-column label="分发方式" width="150">
            <template #default="{ row }">
              <el-tag
                :type="distributionTypeTag[row.distribution_type]"
                class="rounded-full"
              >
                {{ distributionTypeLabels[row.distribution_type] }}
                <template v-if="row.distribution_type === 'coin_pull'">
                  ({{ row.pull_price }}金币)
                </template>
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="使用方式" width="150">
            <template #default="{ row }">
              <el-tag :type="usageTypeTag[row.usage_type]" class="rounded-full">
                {{ usageTypeLabels[row.usage_type] }}
                <template v-if="row.usage_type === 'coin'">
                  ({{ row.usage_price }}金币/次)
                </template>
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusTag[row.status]" class="rounded-full">
                {{ statusLabels[row.status] }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <div class="flex items-center space-x-2">
                <el-tooltip content="查看详情" placement="top">
                  <el-button
                    link
                    type="primary"
                    @click="viewDetails(row)"
                    class="!flex !items-center"
                  >
                    <i-lucide-eye class="w-4 h-4 mr-1" />
                    查看
                  </el-button>
                </el-tooltip>

                <template v-if="row.status === 'pending'">
                  <el-tooltip content="通过审核" placement="top">
                    <el-button
                      link
                      type="success"
                      @click="handleApprove(row)"
                      class="!flex !items-center"
                    >
                      <i-lucide-check class="w-4 h-4 mr-1" />
                      通过
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="拒绝审核" placement="top">
                    <el-button
                      link
                      type="danger"
                      @click="handleReject(row)"
                      class="!flex !items-center"
                    >
                      <i-lucide-x class="w-4 h-4 mr-1" />
                      拒绝
                    </el-button>
                  </el-tooltip>
                </template>

                <template v-if="row.status === 'approved'">
                  <el-tooltip content="下架模型" placement="top">
                    <el-button
                      link
                      type="danger"
                      @click="handleDelist(row)"
                      class="!flex !items-center"
                    >
                      <i-lucide-arrow-down-to-line class="w-4 h-4 mr-1" />
                      下架
                    </el-button>
                  </el-tooltip>
                </template>

                <template v-if="row.status === 'delisted'">
                  <el-tooltip content="重新上架" placement="top">
                    <el-button
                      link
                      type="success"
                      @click="handleList(row)"
                      class="!flex !items-center"
                    >
                      <i-lucide-arrow-up-to-line class="w-4 h-4 mr-1" />
                      上架
                    </el-button>
                  </el-tooltip>
                </template>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 移动端卡片视图 -->
      <div class="md:hidden">
        <div
          v-for="model in models"
          :key="model.id"
          class="bg-white rounded-xl shadow-sm mb-4 p-4"
        >
          <div class="flex items-start mb-3">
            <el-image
              v-if="model.icon"
              :src="model.icon"
              class="w-10 h-10 rounded mr-3 flex-shrink-0"
              :preview-src-list="[model.icon]"
            />
            <div class="flex-1 min-w-0">
              <div class="font-medium text-lg mb-1">{{ model.name }}</div>
              <div class="text-gray-500 text-sm truncate">
                {{ model.description }}
              </div>
            </div>
          </div>

          <div class="space-y-2 mb-3">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">创建者</span>
              <span>{{ model.creator_username }}</span>
            </div>

            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">分发方式</span>
              <el-tag
                :type="distributionTypeTag[model.distribution_type]"
                size="small"
                class="rounded-full"
              >
                {{ distributionTypeLabels[model.distribution_type] }}
                <template v-if="model.distribution_type === 'coin_pull'">
                  ({{ model.pull_price }}金币)
                </template>
              </el-tag>
            </div>

            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">使用方式</span>
              <el-tag
                :type="usageTypeTag[model.usage_type]"
                size="small"
                class="rounded-full"
              >
                {{ usageTypeLabels[model.usage_type] }}
                <template v-if="model.usage_type === 'coin'">
                  ({{ model.usage_price }}金币/次)
                </template>
              </el-tag>
            </div>

            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">状态</span>
              <el-tag
                :type="statusTag[model.status]"
                size="small"
                class="rounded-full"
              >
                {{ statusLabels[model.status] }}
              </el-tag>
            </div>

            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">创建时间</span>
              <span>{{ formatDate(model.created_at) }}</span>
            </div>
          </div>

          <div class="flex flex-wrap gap-2 pt-3 border-t border-gray-100">
            <el-button
              size="small"
              type="primary"
              plain
              @click="viewDetails(model)"
              class="!flex !items-center"
            >
              <i-lucide-eye class="w-4 h-4 mr-1" />
              查看详情
            </el-button>

            <template v-if="model.status === 'pending'">
              <el-button
                size="small"
                type="success"
                plain
                @click="handleApprove(model)"
                class="!flex !items-center"
              >
                <i-lucide-check class="w-4 h-4 mr-1" />
                通过
              </el-button>
              <el-button
                size="small"
                type="danger"
                plain
                @click="handleReject(model)"
                class="!flex !items-center"
              >
                <i-lucide-x class="w-4 h-4 mr-1" />
                拒绝
              </el-button>
            </template>

            <template v-if="model.status === 'approved'">
              <el-button
                size="small"
                type="danger"
                plain
                @click="handleDelist(model)"
                class="!flex !items-center"
              >
                <i-lucide-arrow-down-to-line class="w-4 h-4 mr-1" />
                下架
              </el-button>
            </template>

            <template v-if="model.status === 'delisted'">
              <el-button
                size="small"
                type="success"
                plain
                @click="handleList(model)"
                class="!flex !items-center"
              >
                <i-lucide-arrow-up-to-line class="w-4 h-4 mr-1" />
                上架
              </el-button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="mt-4 flex justify-center md:justify-end">
      <el-pagination
        v-model:currentPage="page"
        v-model:pageSize="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        :layout="
          isMobile ? 'prev, pager, next' : 'total, sizes, prev, pager, next'
        "
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailsVisible"
      :title="selectedModel?.name"
      :width="isMobile ? '90%' : '800px'"
      destroy-on-close
      class="market-model-dialog"
    >
      <template v-if="selectedModel">
        <el-descriptions :column="isMobile ? 1 : 2" border>
          <el-descriptions-item label="创建者">
            {{ selectedModel.creator_username }}
          </el-descriptions-item>

          <el-descriptions-item label="创建时间">
            {{ formatDate(selectedModel.created_at) }}
          </el-descriptions-item>

          <el-descriptions-item label="描述" :span="2">
            {{ selectedModel.description }}
          </el-descriptions-item>

          <el-descriptions-item label="API地址" :span="2">
            {{ selectedModel.api_base_url }}
          </el-descriptions-item>

          <el-descriptions-item label="分发方式">
            {{ distributionTypeLabels[selectedModel.distribution_type] }}
            <template v-if="selectedModel.pull_price">
              ({{ selectedModel.pull_price }}金币)
            </template>
          </el-descriptions-item>

          <el-descriptions-item label="使用方式">
            {{ usageTypeLabels[selectedModel.usage_type] }}
            <template v-if="selectedModel.usage_price">
              ({{ selectedModel.usage_price }}金币/次)
            </template>
          </el-descriptions-item>

          <el-descriptions-item label="拉取次数">
            {{ selectedModel.pull_count }}
          </el-descriptions-item>

          <el-descriptions-item label="使用次数">
            {{ selectedModel.usage_count }}
          </el-descriptions-item>

          <el-descriptions-item label="评分" :span="2">
            <el-rate
              v-model="selectedModel.rating"
              disabled
              show-score
              text-color="#ff9900"
            />
          </el-descriptions-item>
        </el-descriptions>

        <!-- 测试面板 -->
        <div class="test-panel mt-4 p-4 bg-gray-50 rounded-xl">
          <h3 class="font-bold mb-2">模型测试</h3>
          <el-form :model="testForm" label-position="top">
            <el-form-item label="测试消息">
              <el-input
                v-model="testForm.message"
                type="textarea"
                :rows="isMobile ? 3 : 4"
                placeholder="请输入测试消息"
                :disabled="testing"
              />
            </el-form-item>
          </el-form>
          <div class="mb-4">
            <el-button
              type="primary"
              @click="testModel"
              :loading="testing"
              :disabled="!testForm.message"
            >
              发送测试
            </el-button>
          </div>

          <!-- 测试结果展示 -->
          <template v-if="testResult">
            <div
              class="test-result bg-white p-4 rounded-xl border border-gray-200"
            >
              <h4 class="font-bold mb-2">测试结果</h4>
              <template v-if="testResult.status === 'success'">
                <div class="mb-2">
                  <span class="font-bold">响应延迟：</span>
                  {{ testResult.latency }}ms
                </div>
                <div>
                  <span class="font-bold">响应内容：</span>
                  <div class="whitespace-pre-wrap mt-2 p-3 bg-gray-50 rounded">
                    {{ testResult.response || "无响应内容" }}
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="text-red-500">
                  <div class="mb-2">
                    <span class="font-bold">错误：</span>
                    {{ testResult.error }}
                  </div>
                  <div v-if="testResult.latency">
                    <span class="font-bold">响应延迟：</span>
                    {{ testResult.latency }}ms
                  </div>
                </div>
              </template>
            </div>
          </template>
        </div>
      </template>
    </el-dialog>

    <!-- 全局加载状态 -->
    <el-loading
      v-model:full-screen="fullscreenLoading"
      :lock="true"
      text="请稍候..."
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { request } from "@/utils/request";

// 响应式状态
const windowWidth = ref(window.innerWidth);
const isMobile = computed(() => windowWidth.value < 768);

// 监听窗口大小变化
const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

// 状态变量
const loading = ref(false);
const fullscreenLoading = ref(false);
const status = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const models = ref([]);
const detailsVisible = ref(false);
const selectedModel = ref(null);
const testing = ref(false);
const testForm = ref({
  message: "",
});
const testResult = ref(null);

// 常量定义
const distributionTypeLabels = {
  free_pull: "免费拉取",
  coin_pull: "金币拉取",
  key_pull: "兑换码拉取",
};

const distributionTypeTag = {
  free_pull: "success",
  coin_pull: "warning",
  key_pull: "info",
};

const usageTypeLabels = {
  free: "免费使用",
  coin: "按次付费",
};

const usageTypeTag = {
  free: "success",
  coin: "warning",
};

const statusLabels = {
  pending: "待审核",
  approved: "已通过",
  rejected: "已拒绝",
  delisted: "已下架",
};

const statusTag = {
  pending: "warning",
  approved: "success",
  rejected: "danger",
  delisted: "info",
};

// 方法定义
const loadModels = async () => {
  loading.value = true;
  try {
    const data = await request(
      `/api/market/models?page=${page.value}&page_size=${pageSize.value}${
        status.value ? `&status=${status.value}` : ""
      }`
    );
    models.value = data.data;
    total.value = data.total;
  } catch (error) {
    ElMessage({
      message: error.response?.statusText || "加载模型列表失败",
      type: "error",
      plain: true,
      duration: 5000,
    });
  } finally {
    loading.value = false;
  }
};

const formatDate = (date) => {
  if (!date) return "";
  return new Date(date).toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
};

const viewDetails = (model) => {
  selectedModel.value = model;
  testForm.value.message = "";
  testResult.value = null;
  detailsVisible.value = true;
};

const handleApprove = async (model) => {
  try {
    await ElMessageBox.confirm("确定要通过这个模型吗？", "确认操作", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "info",
    });

    fullscreenLoading.value = true;
    await request(`/api/admin/market/models/${model.id}/audit?action=approve`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    ElMessage({
      message: "审核通过成功",
      type: "success",
      plain: true,
      duration: 3000,
    });
    await loadModels();
  } catch (error) {
    if (error.message !== "cancel") {
      ElMessage({
        message: error.response?.statusText || "审核操作失败",
        type: "error",
        plain: true,
        duration: 5000,
      });
    }
  } finally {
    fullscreenLoading.value = false;
  }
};

const handleReject = async (model) => {
  try {
    await ElMessageBox.confirm("确定要拒绝这个模型吗？", "确认操作", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "info",
    });

    fullscreenLoading.value = true;
    await request(`/api/admin/market/models/${model.id}/audit?action=reject`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    ElMessage({
      message: "拒绝成功",
      type: "success",
      plain: true,
      duration: 3000,
    });
    await loadModels();
  } catch (error) {
    if (error.message !== "cancel") {
      ElMessage({
        message: error.response?.statusText || "拒绝操作失败",
        type: "error",
        plain: true,
        duration: 5000,
      });
    }
  } finally {
    fullscreenLoading.value = false;
  }
};

const handleDelist = async (model) => {
  try {
    await ElMessageBox.confirm(
      "确定要下架这个模型吗？下架后用户将无法使用该模型。",
      "确认下架",
      {
        confirmButtonText: "确定下架",
        cancelButtonText: "取消",
        type: "warning",
        confirmButtonClass: "el-button--danger",
      }
    );

    fullscreenLoading.value = true;
    await request(`/api/admin/market/models/${model.id}/delist`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    ElMessage({
      message: "模型已成功下架",
      type: "success",
      plain: true,
      duration: 3000,
    });

    await loadModels();
  } catch (error) {
    if (error.message !== "cancel") {
      ElMessage({
        message: error.response?.statusText || "下架操作失败",
        type: "error",
        plain: true,
        duration: 5000,
      });
    }
  } finally {
    fullscreenLoading.value = false;
  }
};

const handleList = async (model) => {
  try {
    await ElMessageBox.confirm(
      "确定要重新上架这个模型吗？重新上架后需要重新审核。",
      "确认上架",
      {
        confirmButtonText: "确定上架",
        cancelButtonText: "取消",
        type: "info",
      }
    );

    fullscreenLoading.value = true;
    await request(`/api/admin/market/models/${model.id}/list`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    ElMessage({
      message: "模型已成功上架，等待审核",
      type: "success",
      plain: true,
      duration: 3000,
    });

    await loadModels();
  } catch (error) {
    if (error.message !== "cancel") {
      ElMessage({
        message: error.response?.statusText || "上架操作失败",
        type: "error",
        plain: true,
        duration: 5000,
      });
    }
  } finally {
    fullscreenLoading.value = false;
  }
};

const testModel = async () => {
  if (!selectedModel.value || !testForm.value.message) return;

  testing.value = true;
  testResult.value = null;

  try {
    const response = await request(
      `/api/admin/market/models/${selectedModel.value.id}/test`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: testForm.value.message,
        }),
      }
    );

    testResult.value = {
      status: "success",
      response:
        response.response?.choices?.[0]?.message?.content || "No content",
      latency: response.latency,
    };

    ElMessage({
      message: "测试完成",
      type: "success",
      plain: true,
      duration: 3000,
    });
  } catch (error) {
    try {
      const errorData = await error.response.json();
      let errorMessage = "测试失败";

      if (errorData.detail) {
        if (typeof errorData.detail === "string") {
          errorMessage = errorData.detail;
        } else if (errorData.detail.message) {
          errorMessage = errorData.detail.message;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail
            .map((err) => err.msg || err.message)
            .join("\n");
        }
      }

      ElMessage({
        message: errorMessage,
        type: "error",
        duration: 5000,
        plain: true,
        showClose: true,
      });

      testResult.value = {
        status: "error",
        error: errorMessage,
        latency: errorData.detail.latency || 0,
      };
    } catch (parseError) {
      ElMessage({
        message: error.message || "请求失败",
        type: "error",
        duration: 5000,
        plain: true,
        showClose: true,
      });
    }
  } finally {
    testing.value = false;
  }
};

const handleSizeChange = (val) => {
  pageSize.value = val;
  loadModels();
};

const handleCurrentChange = (val) => {
  page.value = val;
  loadModels();
};

// 生命周期钩子
onMounted(() => {
  window.addEventListener("resize", handleResize);
  loadModels();
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
.market-models-review {
  @apply p-4 sm:p-6;
}

.header-section {
  @apply mb-6;
}

.model-list-section {
  @apply bg-white rounded-xl shadow-sm;
}

/* 表格样式 */
:deep(.el-table) {
  @apply rounded-xl overflow-hidden;
}

:deep(.el-table__header) {
  @apply bg-gray-50;
}

:deep(.el-table__row) {
  @apply transition-colors duration-200;
}

:deep(.el-table__row:hover) {
  @apply bg-gray-50;
}

/* 操作按钮样式 */
:deep(.el-button--link) {
  @apply p-1 rounded-md;
}

:deep(.el-button--link:hover) {
  @apply bg-gray-100;
}

/* 状态标签样式 */
:deep(.el-tag) {
  @apply rounded-md px-2 py-1;
}

/* 分页器样式 */
:deep(.el-pagination) {
  @apply py-4;
}

/* 对话框样式 */
:deep(.el-dialog) {
  @apply rounded-2xl overflow-hidden;
}

:deep(.el-dialog__header) {
  @apply m-0 p-4 border-b border-gray-200 bg-gray-50;
}

:deep(.el-dialog__body) {
  @apply p-6;
}

:deep(.el-descriptions) {
  @apply p-4 rounded-xl bg-gray-50;
}

/* 测试面板样式 */
.test-panel {
  @apply bg-gray-50 rounded-xl p-4 mt-4 border border-gray-200;
}

.test-panel .el-button {
  @apply mt-3;
}

.test-result {
  @apply bg-white rounded-xl p-4 mt-4 shadow-sm border border-gray-200;
}

/* 移动端样式优化 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    @apply w-11/12 max-w-none m-auto;
  }

  :deep(.el-dialog__body) {
    @apply p-4;
  }

  .test-panel {
    @apply p-3;
  }

  :deep(.el-descriptions-item) {
    @apply p-2;
  }
}
</style>
