<template>
  <div class="p-4 sm:p-6 space-y-6 sm:space-y-8 bg-white min-h-screen">
    <!-- 统计卡片 -->
    <div
      class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 sm:gap-6"
    >
      <div
        v-for="card in statsCards"
        :key="card.key"
        class="relative overflow-hidden rounded-xl sm:rounded-2xl shadow-lg transition-all duration-300 hover:scale-105"
        :class="card.bgColor"
        @mouseenter="hoveredCard = card.key"
        @mouseleave="hoveredCard = null"
      >
        <div class="p-4 sm:p-6">
          <div class="flex items-center space-x-3 sm:space-x-4">
            <div
              :class="[
                card.color,
                'p-2 sm:p-3 rounded-full transition-transform duration-300',
                hoveredCard === card.key
                  ? 'transform -translate-y-1 sm:-translate-y-2'
                  : '',
              ]"
            >
              <component
                :is="card.icon"
                class="w-5 h-5 sm:w-6 sm:h-6 text-white"
              />
            </div>
            <div>
              <div class="text-xs sm:text-sm font-medium text-gray-600">
                {{ card.title }}
              </div>
              <div class="text-lg sm:text-2xl font-bold text-gray-800">
                {{ stats[card.key] || "0" }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
      <!-- 模型使用分布图 -->
      <div class="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6">
        <h3 class="text-base sm:text-lg font-semibold mb-4">模型使用分布</h3>
        <div class="h-96 sm:h-80">
          <DoughnutChart :data="modelUsageData" title="模型调用次数占比" />
        </div>
      </div>

      <!-- 成功失败分布图 -->
      <div class="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6">
        <h3 class="text-base sm:text-lg font-semibold mb-4">请求结果分布</h3>
        <div class="h-96 sm:h-80">
          <DoughnutChart :data="requestStatusData" title="成功/失败比例" />
        </div>
      </div>
    </div>

    <!-- 筛选器 移动端优化 -->
    <div class="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6">
      <div
        class="flex flex-col sm:flex-row gap-4 items-stretch sm:items-center"
      >
        <ElSelect
          v-model="filters.model"
          placeholder="选择模型"
          clearable
          class="!w-full sm:!w-40"
        >
          <ElOption
            v-for="model in modelOptions"
            :key="model"
            :label="model"
            :value="model"
          />
        </ElSelect>

        <ElDatePicker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DDTHH:mm:ss[Z]"
          class="!w-full"
        />

        <div class="flex gap-3 sm:ml-auto">
          <button
            class="flex-1 sm:flex-none px-4 sm:px-6 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-all duration-200"
            @click="handleFilter"
          >
            筛选
          </button>

          <button
            class="flex-1 sm:flex-none px-4 sm:px-6 py-2 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-all duration-200"
            @click="resetFilter"
          >
            重置
          </button>
        </div>
      </div>
    </div>

    <!-- 日志表格 -->
    <div class="bg-white rounded-xl sm:rounded-2xl shadow-lg overflow-hidden">
      <div class="relative min-h-[400px]">
        <!-- 加载动画 -->
        <div
          v-if="loading"
          class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10"
        >
          <div
            class="w-12 h-12 sm:w-16 sm:h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"
          />
        </div>

        <!-- 桌面端表格 -->
        <div class="hidden sm:block">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  v-for="header in [
                    '时间',
                    '模型',
                    'Token数',
                    '响应时间',
                    '',
                    '状态',
                  ]"
                  :key="header"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {{ header }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="log in logs"
                :key="log.id"
                class="hover:bg-gray-50 transition-colors duration-150"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(log.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  {{ log.model_name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  {{ log.total_tokens }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  {{ Math.round(log.total_latency) }}ms
                </td>
                <td
                  class="px-6 py-4 text-sm text-gray-500 truncate max-w-xs"
                  :title="log.request_text"
                >
                  {{ log.request_text }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                      log.error
                        ? 'bg-red-100 text-red-800'
                        : 'bg-green-100 text-green-800',
                    ]"
                  >
                    {{ log.error ? "失败" : "成功" }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 移动端卡片列表 -->
        <div class="block sm:hidden">
          <div class="divide-y divide-gray-200">
            <div v-for="log in logs" :key="log.id" class="p-4 space-y-3">
              <div class="flex justify-between items-start">
                <span class="text-sm text-gray-500">
                  {{ formatDate(log.created_at) }}
                </span>
                <span
                  :class="[
                    'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                    log.error
                      ? 'bg-red-100 text-red-800'
                      : 'bg-green-100 text-green-800',
                  ]"
                >
                  {{ log.error ? "失败" : "成功" }}
                </span>
              </div>

              <div class="flex justify-between items-center text-sm">
                <span class="font-medium">{{ log.model_name }}</span>
                <div class="space-x-4 text-gray-500">
                  <span>{{ log.total_tokens }} tokens</span>
                  <span>{{ Math.round(log.total_latency) }}ms</span>
                </div>
              </div>

              <p class="text-sm text-gray-500 break-words">
                {{ log.request_text }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页器 -->
      <div class="px-4 sm:px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div
          class="flex flex-col sm:flex-row items-center justify-between gap-4"
        >
          <span class="text-sm text-gray-700 order-2 sm:order-1"
            >共 {{ total }} 条记录</span
          >
          <div
            class="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto order-1 sm:order-2"
          >
            <select
              v-model="pagination.pageSize"
              class="w-full sm:w-auto border border-gray-300 rounded-full px-4 py-2 text-sm"
              @change="handleSizeChange($event.target.value)"
            >
              <option value="10">10条/页</option>
              <option value="20">20条/页</option>
              <option value="50">50条/页</option>
            </select>

            <div class="flex items-center gap-2 w-full sm:w-auto">
              <button
                class="flex-1 sm:flex-none px-4 py-2 border rounded-full text-sm disabled:opacity-50"
                :disabled="pagination.currentPage === 1"
                @click="handlePageChange(pagination.currentPage - 1)"
              >
                上一页
              </button>
              <span class="text-sm whitespace-nowrap"
                >第 {{ pagination.currentPage }} 页</span
              >
              <button
                class="flex-1 sm:flex-none px-4 py-2 border rounded-full text-sm disabled:opacity-50"
                :disabled="
                  pagination.currentPage * pagination.pageSize >= total
                "
                @click="handlePageChange(pagination.currentPage + 1)"
              >
                下一页
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage, ElDatePicker, ElSelect, ElOption } from "element-plus";
import {
  MessageSquare,
  Clock,
  Zap,
  AlertCircle,
  Settings,
} from "lucide-vue-next";
import { request } from "@/utils/request";
import DoughnutChart from "@/components/chart/DoughnutChart.vue";

// 统计数据
const stats = ref({
  total_requests: 0,
  total_tokens: 0,
  avg_tokens: 0,
  avg_latency: 0,
  error_rate: 0,
});

// 图表数据
const modelUsageData = ref([]);
const requestStatusData = ref([]);

// 日志数据
const logs = ref([]);
const loading = ref(false);
const total = ref(0);
const hoveredCard = ref(null);
const modelOptions = ref([]);

// 统计卡片配置
const statsCards = [
  {
    title: "总请求数",
    key: "total_requests",
    icon: MessageSquare,
    color: "bg-blue-500",
    bgColor: "bg-blue-50",
  },
  {
    title: "总Token数",
    key: "total_tokens",
    icon: Zap,
    color: "bg-yellow-500",
    bgColor: "bg-yellow-50",
  },
  {
    title: "平均Token",
    key: "avg_tokens",
    icon: Settings,
    color: "bg-green-500",
    bgColor: "bg-green-50",
  },
  {
    title: "平均响应时间",
    key: "avg_latency",
    icon: Clock,
    color: "bg-purple-500",
    bgColor: "bg-purple-50",
  },
  {
    title: "错误率",
    key: "error_rate",
    icon: AlertCircle,
    color: "bg-red-500",
    bgColor: "bg-red-50",
  },
];

// 分页配置
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
});

// 筛选条件
const filters = ref({
  model: "",
  dateRange: [],
});

// 获取统计数据
const fetchStats = async () => {
  try {
    const params = new URLSearchParams();
    if (filters.value.dateRange?.[0]) {
      params.append("start_date", filters.value.dateRange[0]);
    }
    if (filters.value.dateRange?.[1]) {
      params.append("end_date", filters.value.dateRange[1]);
    }

    const response = await request(`/api/user/ai-logs/stats?${params}`);
    const errorRate = response.error_rate * 100;

    Object.assign(stats.value, {
      total_requests: response.total_requests,
      total_tokens: response.total_tokens,
      avg_tokens: Math.round(response.avg_tokens),
      avg_latency: Math.round(response.avg_latency),
      error_rate: errorRate.toFixed(2) + "%",
    });

    // 更新模型使用数据
    modelUsageData.value = response.models_usage.map((item) => ({
      label: item.model,
      value: item.count,
    }));

    // 更新请求状态数据
    const successCount =
      response.total_requests - response.total_requests * response.error_rate;
    const failureCount = response.total_requests * response.error_rate;
    requestStatusData.value = [
      { label: "成功请求", value: Math.round(successCount) },
      { label: "失败请求", value: Math.round(failureCount) },
    ];

    // 更新模型选项
    const uniqueModels = new Set(
      response.models_usage.map((item) => item.model)
    );
    modelOptions.value = Array.from(uniqueModels);
  } catch (error) {
    ElMessage.error({
      message: "获取统计数据失败",
      plain: true,
    });
  }
};

// 获取日志记录
const fetchLogs = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({
      skip: (
        (pagination.value.currentPage - 1) *
        pagination.value.pageSize
      ).toString(),
      limit: pagination.value.pageSize.toString(),
    });

    if (filters.value.model) {
      params.append("model_name", filters.value.model);
    }
    if (filters.value.dateRange?.[0]) {
      params.append("start_date", filters.value.dateRange[0]);
    }
    if (filters.value.dateRange?.[1]) {
      params.append("end_date", filters.value.dateRange[1]);
    }

    const response = await request(`/api/user/ai-logs?${params}`);
    logs.value = response.items;
    total.value = response.total;
  } catch (error) {
    ElMessage.error({
      message: "获取日志记录失败",
      plain: true,
    });
  } finally {
    loading.value = false;
  }
};

// 处理筛选
const handleFilter = () => {
  pagination.value.currentPage = 1;
  fetchStats();
  fetchLogs();
};

// 重置筛选
const resetFilter = () => {
  filters.value = {
    model: "",
    dateRange: [],
  };
  handleFilter();
};

// 分页处理
const handlePageChange = (newPage) => {
  pagination.value.currentPage = newPage;
  fetchLogs();
};

const handleSizeChange = (newSize) => {
  pagination.value.pageSize = parseInt(newSize);
  pagination.value.currentPage = 1;
  fetchLogs();
};

// 格式化时间
const formatDate = (date) => {
  return new Date(date).toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
};

onMounted(() => {
  fetchStats();
  fetchLogs();
});
</script>

<style scoped>
/* ElDatePicker 在移动端下的样式调整 */
:deep(.el-date-editor.el-input) {
  @apply !w-full;
}

:deep(.el-date-editor.el-input__wrapper) {
  @apply !w-full;
}

:deep(.el-range-editor.el-input__wrapper) {
  @apply !w-full;
}

/* Element Plus 组件样式优化 */
:deep(.el-select-dropdown) {
  @apply !rounded-lg;
}

:deep(.el-picker-panel) {
  @apply !rounded-lg;
}

/* 触摸设备交互优化 */
@media (hover: none) {
  .hover\:bg-blue-600:active {
    @apply bg-blue-600;
  }

  .hover\:bg-gray-200:active {
    @apply bg-gray-200;
  }
}
</style>
