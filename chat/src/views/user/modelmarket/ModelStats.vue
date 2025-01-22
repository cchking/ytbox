#src/views/user/modelmarket/ModelStats.vue
<template>
  <div class="space-y-6">
    <!-- 请求统计图表 -->
    <div class="bg-gray-50 rounded-lg p-4 sm:p-6">
      <h2 class="text-base sm:text-lg font-bold mb-4">请求统计</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <!-- 饼图 -->
        <div class="h-64">
          <DoughnutChart :data="chartData" title="请求成功率" />
        </div>
        <!-- 基础统计信息 -->
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-white p-4 rounded-lg">
              <div class="text-sm text-gray-500">总请求次数</div>
              <div class="text-xl font-medium">{{ stats.total_requests }}</div>
            </div>
            <div class="bg-white p-4 rounded-lg">
              <div class="text-sm text-gray-500">错误次数</div>
              <div class="text-xl font-medium">{{ stats.error_count }}</div>
            </div>
            <div class="bg-white p-4 rounded-lg">
              <div class="text-sm text-gray-500">平均延迟</div>
              <div class="text-xl font-medium">
                {{ (stats.avg_latency / 1000).toFixed(2) }}s
              </div>
            </div>
            <div class="bg-white p-4 rounded-lg">
              <div class="text-sm text-gray-500">总token数</div>
              <div class="text-xl font-medium">{{ stats.total_tokens }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误请求列表 -->
    <div v-if="errorLogs.length > 0" class="bg-gray-50 rounded-lg p-3 sm:p-6">
      <h2 class="text-base sm:text-lg font-bold mb-3 sm:mb-4">错误请求列表</h2>
      <div class="space-y-3">
        <el-card
          v-for="log in errorLogs"
          :key="log.id"
          shadow="hover"
          class="box-card !border-none"
        >
          <template #header>
            <div class="flex justify-between items-center">
              <div class="text-xs sm:text-sm text-gray-500">
                {{ formatDate(log.created_at) }}
              </div>
              <el-tag type="danger" size="small">错误请求</el-tag>
            </div>
          </template>
          <!-- 错误信息 -->
          <div class="space-y-3">
            <!-- 请求信息 -->
            <el-collapse class="!border-0">
              <el-collapse-item>
                <template #title>
                  <span class="text-sm">请求信息</span>
                </template>
                <div
                  class="bg-gray-50 p-2 rounded text-xs sm:text-sm space-y-2"
                >
                  <div>
                    <span class="font-medium">Prompt Tokens:</span>
                    {{ log.prompt_tokens }}
                  </div>
                  <div>
                    <span class="font-medium">Completion Tokens:</span>
                    {{ log.completion_tokens }}
                  </div>
                  <div>
                    <span class="font-medium">Total Latency:</span>
                    {{ (log.total_latency / 1000).toFixed(2) }}s
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>

            <!-- 错误详情 -->
            <div>
              <div class="text-sm mb-1">错误详情：</div>
              <div class="relative">
                <div class="absolute right-2 top-2 z-10">
                  <el-button
                    type="primary"
                    link
                    @click="toggleErrorDetail(log.id)"
                    class="!p-1"
                  >
                    {{ showOriginal[log.id] ? "×" : "查看原始" }}
                  </el-button>
                </div>
                <el-alert
                  :title="getErrorTitle(log.error)"
                  type="error"
                  :description="
                    showOriginal[log.id]
                      ? formatError(log.error)
                      : getErrorDescription(log.error)
                  "
                  show-icon
                  :closable="false"
                />
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import DoughnutChart from "@/components/chart/DoughnutChart.vue";

const props = defineProps({
  model: {
    type: Object,
    required: true,
  },
});

// 计算基础统计数据
const stats = computed(() => {
  return (
    props.model?.logs?.stats || {
      total_requests: 0,
      error_count: 0,
      avg_latency: 0,
      total_tokens: 0,
    }
  );
});

// 计算图表数据
const chartData = computed(() => {
  const { total_requests, error_count } = stats.value;
  const success_count = total_requests - error_count;

  return [
    {
      label: "成功请求",
      value: success_count,
    },
    {
      label: "失败请求",
      value: error_count,
    },
  ];
});

// 获取错误日志
const errorLogs = computed(() => {
  return props.model?.logs?.items?.filter((log) => log.error) || [];
});

// 显示原始信息的状态
const showOriginal = ref({});

// 切换错误详情显示
const toggleErrorDetail = (logId) => {
  showOriginal.value[logId] = !showOriginal.value[logId];
};

// 格式化日期
const formatDate = (date) => {
  if (!date) return "";
  const d = new Date(date);
  if (isNaN(d.getTime())) return "";

  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// 获取错误标题
const getErrorTitle = (errorStr) => {
  try {
    const errorObj = JSON.parse(errorStr);
    const detail = errorObj.detail?.error || {};
    return detail.type || "Error";
  } catch (e) {
    return "Error";
  }
};

// 获取错误描述
const getErrorDescription = (errorStr) => {
  try {
    const errorObj = JSON.parse(errorStr);
    const detail = errorObj.detail?.error || {};
    return detail.message || errorObj.message || errorStr;
  } catch (e) {
    return errorStr;
  }
};

// 格式化错误信息
const formatError = (errorStr) => {
  try {
    const errorObj = JSON.parse(errorStr);
    return JSON.stringify(errorObj, null, 2);
  } catch (e) {
    return errorStr;
  }
};
</script>

<style scoped>
:deep(.el-collapse) {
  --el-collapse-header-height: 32px;
}

:deep(.el-collapse-item__header) {
  border: none;
  padding: 0;
}

:deep(.el-collapse-item__wrap) {
  border: none;
}

:deep(.el-collapse-item__content) {
  padding-bottom: 0;
}

:deep(.el-card__header) {
  padding: 12px 16px;
}

:deep(.el-card__body) {
  padding: 12px 16px;
}

:deep(.el-alert__title) {
  font-size: 13px;
}

:deep(.el-alert__description) {
  margin: 8px 0 0;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}

:deep(.el-alert__close-btn) {
  top: 8px;
}

@media (max-width: 640px) {
  :deep(.el-card__header) {
    padding: 10px 12px;
  }

  :deep(.el-card__body) {
    padding: 10px 12px;
  }
}
</style>
