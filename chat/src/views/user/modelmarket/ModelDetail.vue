#src\views\user\modelmarket\ModelDetail.vue
<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-[100]">
      <!-- 遮罩层 -->
      <div
        class="absolute inset-0 bg-black bg-opacity-50"
        @click="handleClose"
      ></div>

      <!-- 内容区域 -->
      <div class="relative w-full h-full bg-white overflow-auto">
        <div class="detail-container min-h-screen p-4 sm:p-6">
          <!-- 返回按钮 -->
          <div
            class="flex items-center mb-4 cursor-pointer"
            @click="handleClose"
          >
            <ArrowLeft class="w-5 h-5 text-gray-500 mr-2" />
            <span class="text-gray-600">返回</span>
          </div>

          <div v-if="model">
            <!-- 基本信息 -->
            <div class="mb-6 sm:mb-8 pt-4">
              <div class="flex gap-4">
                <img
                  :src="model.icon || '/placeholder.png'"
                  class="w-20 h-20 sm:w-24 sm:h-24 rounded-lg object-cover shrink-0"
                />
                <div class="min-w-0 flex-1">
                  <h1 class="text-xl sm:text-2xl font-bold mb-2">
                    {{ model.name }}
                  </h1>
                  <div class="flex items-center gap-2 flex-wrap">
                    <el-tag
                      :type="getTagType(model)"
                      size="small"
                      class="sm:hidden"
                    >
                      {{ getPriceText(model) }}
                    </el-tag>
                    <p class="text-gray-600 text-sm">
                      由 {{ model.creator?.username }} 创建
                    </p>
                    <p class="text-gray-500 text-sm">
                      创建于 {{ formatDate(model.created_at) }}
                    </p>
                  </div>
                  <div class="mt-2 sm:hidden text-sm text-gray-600">
                    {{ getDistributionTypeText(model.distribution_type) }}
                    {{
                      model.usage_type === "free"
                        ? "· 免费使用"
                        : `· ${model.usage_price}金币/次`
                    }}
                  </div>
                </div>
                <el-tag
                  :type="getTagType(model)"
                  size="large"
                  class="hidden sm:flex self-start shrink-0"
                >
                  {{ getPriceText(model) }}
                </el-tag>
              </div>
            </div>

            <!-- 统计信息 -->
            <div
              class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8"
            >
              <div class="bg-gray-50 rounded-lg p-3 sm:p-4">
                <div class="text-xs sm:text-sm text-gray-500 mb-1">评分</div>
                <div class="flex items-center">
                  <el-rate
                    v-model="model.stats.rating"
                    disabled
                    text-color="#A1A1A1"
                    size="small"
                    class="sm:hidden"
                  />
                  <el-rate
                    v-model="model.stats.rating"
                    disabled
                    text-color="#A1A1A1"
                    class="hidden sm:flex"
                  />
                  <span class="ml-2 text-base sm:text-lg font-medium">
                    {{ model.stats.rating?.toFixed(1) || "--" }}
                  </span>
                </div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 sm:p-4">
                <div class="text-xs sm:text-sm text-gray-500 mb-1">
                  拉取次数
                </div>
                <div class="text-base sm:text-lg font-medium">
                  {{ model.stats.pull_count }}
                </div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 sm:p-4">
                <div class="text-xs sm:text-sm text-gray-500 mb-1">
                  使用次数
                </div>
                <div class="text-base sm:text-lg font-medium">
                  {{ model.stats.usage_count }}
                </div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 sm:p-4">
                <div class="text-xs sm:text-sm text-gray-500 mb-1">
                  本月使用
                </div>
                <div class="text-base sm:text-lg font-medium">
                  {{ model.stats.monthly_usage }}
                </div>
              </div>
            </div>

            <!-- 评分分布 -->
            <div class="mb-6 sm:mb-8 bg-gray-50 rounded-lg p-4 sm:p-6">
              <h2 class="text-base sm:text-lg font-bold mb-4">评分分布</h2>
              <div class="space-y-3">
                <div
                  v-for="rating in [5, 4, 3, 2, 1]"
                  :key="rating"
                  class="flex items-center gap-3 sm:gap-4"
                >
                  <div class="w-10 sm:w-12 text-xs sm:text-sm">
                    {{ rating }}星
                  </div>
                  <div class="flex-1 bg-gray-200 rounded-full h-1.5 sm:h-2">
                    <div
                      class="bg-primary h-full rounded-full"
                      :style="{
                        width: `${getDistributionPercentage(rating)}%`,
                      }"
                    ></div>
                  </div>
                  <div
                    class="w-12 sm:w-16 text-right text-xs sm:text-sm text-gray-500"
                  >
                    {{ reviewStats.rating_distribution?.[rating] || 0 }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 使用信息 -->
            <div class="mb-6 sm:mb-8">
              <h2 class="text-base sm:text-lg font-bold mb-4">使用信息</h2>
              <el-descriptions :column="1" :column-sm="2" border>
                <el-descriptions-item label="分发方式">
                  {{ getDistributionTypeText(model.distribution_type) }}
                </el-descriptions-item>
                <el-descriptions-item label="拉取价格">
                  {{
                    model.distribution_type === "coin_pull"
                      ? `${model.pull_price} 金币`
                      : "-"
                  }}
                </el-descriptions-item>
                <el-descriptions-item label="使用方式">
                  {{ model.usage_type === "free" ? "免费使用" : "付费使用" }}
                </el-descriptions-item>
                <el-descriptions-item label="使用价格">
                  {{
                    model.usage_type === "coin"
                      ? `${model.usage_price} 金币`
                      : "-"
                  }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-4 mb-6 sm:mb-8">
              <el-button
                v-if="!model.user_interaction.has_pulled"
                type="primary"
                @click="handlePull"
                :loading="pulling"
                size="large"
                class="w-full sm:w-auto"
              >
                拉取模型
              </el-button>
            </div>

            <!-- 评论系统 -->
            <ModelComments
              :model-id="modelId"
              :model-creator-id="model.creator?.id"
              :user-has-pulled="model.user_interaction.has_pulled"
              :user-review="model.user_interaction.user_review"
              :review-stats="reviewStats"
              :model-data="model"
              @review-submitted="handleReviewSubmitted"
            />
          </div>

          <!-- 激活码输入对话框 -->
          <el-dialog
            v-model="showKeyInput"
            title="输入激活码"
            width="90%"
            sm:width="400px"
          >
            <el-input v-model="keyCode" placeholder="请输入激活码" />
            <template #footer>
              <el-button @click="showKeyInput = false">取消</el-button>
              <el-button
                type="primary"
                @click="submitKey"
                :loading="submittingKey"
              >
                确认
              </el-button>
            </template>
          </el-dialog>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { ArrowLeft } from "lucide-vue-next";
import { request } from "@/utils/request";
import { useUserStore } from "@/stores/user";
import ModelComments from "./ModelComments.vue";

const props = defineProps({
  modelId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["close"]);
const userStore = useUserStore();

// 状态变量
const visible = ref(true);
const model = ref(null);
const reviewStats = ref({});
const pulling = ref(false);
const showKeyInput = ref(false);
const submittingKey = ref(false);
const keyCode = ref("");

// 处理关闭
const handleClose = () => {
  visible.value = false;
  emit("close");
};

// 获取模型详情
const loadModel = async () => {
  try {
    if (!props.modelId) {
      ElMessage.error({
        message: "无效的模型ID",
        plain: true,
      });
      handleClose();
      return;
    }
    const data = await request(`/api/market/models/${props.modelId}`);
    model.value = data;
  } catch (error) {
    ElMessage.error({
      message: error.response?.data?.detail || "获取模型详情失败",
      plain: true,
    });
    handleClose();
  }
};

// 计算评分分布百分比
const getDistributionPercentage = (rating) => {
  const distribution = reviewStats.value.rating_distribution || {};
  const total = Object.values(distribution).reduce((a, b) => a + b, 0);
  if (!total) return 0;
  return (((distribution[rating] || 0) / total) * 100).toFixed(1);
};

// 拉取模型
const handlePull = async () => {
  if (model.value.distribution_type === "key_pull") {
    showKeyInput.value = true;
    return;
  }

  if (model.value.distribution_type === "coin_pull") {
    try {
      await ElMessageBox.confirm(
        `拉取此模型需要 ${model.value.pull_price} 金币，是否继续？`,
        "确认拉取",
        {
          confirmButtonText: "确认",
          cancelButtonText: "取消",
          type: "warning",
        }
      );
      await doPull();
    } catch (error) {
      if (error !== "cancel") {
        ElMessage.error({
          message: error.response?.data?.detail || "拉取失败",
          plain: true,
        });
      }
    }
  } else {
    await doPull();
  }
};

// 执行拉取
const doPull = async () => {
  pulling.value = true;
  try {
    const requestBody = {
      key_code: keyCode.value || "",
    };

    await request(`/api/market/models/${props.modelId}/pull`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    ElMessage.success({
      message: "模型拉取成功",
      plain: true,
    });

    await loadModel();
    showKeyInput.value = false;
    keyCode.value = "";
  } catch (error) {
    ElMessage.error({
      message: error.response?.data?.detail || "拉取失败",
      plain: true,
    });
  } finally {
    pulling.value = false;
  }
};

// 提交激活码
const submitKey = () => {
  if (!keyCode.value) {
    ElMessage.warning({
      message: "请输入激活码",
      plain: true,
    });
    return;
  }
  doPull();
};

const handleReviewSubmitted = () => {
  loadModel();
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

const getTagType = (model) => {
  if (!model) return "info";

  switch (model.distribution_type) {
    case "free_pull":
      return "info";
    case "coin_pull":
      return "warning";
    case "key_pull":
      return "info";
    default:
      return "info";
  }
};

const getPriceText = (model) => {
  if (!model) return "";

  switch (model.distribution_type) {
    case "free_pull":
      return "免费";
    case "coin_pull":
      return `${model.pull_price}金币`;
    case "key_pull":
      return "激活码";
    default:
      return "";
  }
};

const getDistributionTypeText = (type) => {
  const map = {
    free_pull: "免费拉取",
    coin_pull: "金币拉取",
    key_pull: "激活码拉取",
  };
  return map[type] || type;
};

// 在组件挂载时加载数据
onMounted(() => {
  if (props.modelId) {
    loadModel();
  }
});
</script>

<style scoped>
.detail-container {
  overflow-y: auto;
  max-height: 100vh;
}

.el-descriptions {
  --el-descriptions-item-bordered-label-background: #f8fafc;
}

.bg-primary {
  background-color: var(--el-color-primary);
}

/* 避免手机端评分组件太大 */
:deep(.el-rate__icon) {
  font-size: 16px;
}

@media (min-width: 640px) {
  :deep(.el-rate__icon) {
    font-size: 20px;
  }
}
</style>
