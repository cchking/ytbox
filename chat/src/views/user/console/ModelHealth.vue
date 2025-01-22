<template>
  <div class="model-status-container">
    <h1 class="text-xl md:text-2xl font-semibold mb-4 md:mb-6">
      模型健康状态(仅供参考)
    </h1>

    <!-- 功能未启用提示 -->
    <div
      v-if="healthData?.enabled === false"
      class="bg-white rounded-lg shadow-sm p-8 text-center"
    >
      <div class="flex justify-center mb-4">
        <div class="shrug-icon text-4xl">¯\_(ツ)_/¯</div>
      </div>
      <div class="text-gray-600 mb-2 text-lg">管理员暂未开启此功能</div>
      <div class="text-sm text-gray-400">{{ healthData.message }}</div>
    </div>

    <!-- 原有内容 -->
    <template v-else>
      <!-- 搜索栏 - 移动端优化 -->
      <div class="bg-white p-3 md:p-4 rounded-lg shadow-sm mb-4 md:mb-6">
        <div class="flex flex-col sm:flex-row gap-3 md:gap-4">
          <div class="w-full sm:flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索模型名称..."
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
          <div class="w-full sm:w-[150px]">
            <select
              v-model="statusFilter"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 text-sm"
            >
              <option value="all">全部状态</option>
              <option value="success">正常</option>
              <option value="error">异常</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="text-gray-500">加载中...</div>
      </div>

      <!-- 错误状态 -->
      <div v-if="error" class="error-state">
        <div>{{ error }}</div>
      </div>

      <!-- 数据展示 -->
      <div
        v-if="!loading && !error && healthData?.models"
        class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-6"
      >
        <div
          v-for="(model, index) in filteredModels"
          :key="model.model_name + index"
          class="model-card bg-white rounded-lg shadow-sm p-4 md:p-5"
        >
          <!-- 状态头部 -->
          <div class="flex justify-between items-center mb-4 flex-wrap gap-2">
            <div class="flex items-center gap-3 min-w-[180px]">
              <span
                class="status-badge"
                :class="{ success: model.success_rate >= 95 }"
              >
                {{ Math.round(model.success_rate) }}%
              </span>
              <span class="model-name truncate">{{ model.model_name }}</span>
            </div>
            <span
              class="channel-name text-xs md:text-sm text-gray-500 truncate"
            >
              {{ model.channel_name }}
            </span>
          </div>

          <!-- 状态历史条 -->
          <div v-if="model.trend?.length" class="status-timeline">
            <div class="timeline-info">
              <span class="text-xs text-gray-500">{{
                formatTime(model.trend[0].timestamp)
              }}</span>
              <span class="text-xs text-gray-500">now</span>
            </div>
            <div class="status-bars">
              <div
                v-for="(point, idx) in model.trend"
                :key="idx"
                class="status-bar-wrapper"
              >
                <div
                  class="status-bar"
                  :class="point.status === 'success' ? 'healthy' : 'error'"
                  :style="{
                    height: `${calculateHeight(
                      point.latency,
                      model.avg_latency
                    )}%`,
                    minHeight: '10%',
                  }"
                  :title="getTooltipContent(point)"
                />
              </div>
            </div>
          </div>

          <!-- 指标统计 -->
          <div class="grid grid-cols-3 gap-3 mt-6">
            <div class="text-center">
              <p class="text-xs text-gray-500 mb-1">平均延迟</p>
              <p class="text-sm font-medium">
                {{ Math.round(model.avg_latency) }}ms
              </p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500 mb-1">当前延迟</p>
              <p class="text-sm font-medium">
                {{ Math.round(model.current_latency) }}ms
              </p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500 mb-1">检查总数</p>
              <p class="text-sm font-medium">{{ model.total_checks }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="text-right text-xs text-gray-500 mt-4">
        最后更新: {{ new Date().toLocaleTimeString() }}
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { request } from "@/utils/request";

const healthData = ref(null);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref("");
const statusFilter = ref("all");
let refreshInterval = null;

// 计算筛选后的模型列表
const filteredModels = computed(() => {
  if (!healthData.value?.models) return [];

  return healthData.value.models.filter((model) => {
    // 名称搜索
    const nameMatch = model.model_name
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase());

    // 状态筛选
    let statusMatch = true;
    if (statusFilter.value !== "all") {
      statusMatch = model.current_status === statusFilter.value;
    }

    return nameMatch && statusMatch;
  });
});

const calculateHeight = (latency, avgLatency) => {
  const baseHeight = 60;
  const ratio = latency / avgLatency;
  return Math.max(10, Math.min(100, ratio * baseHeight));
};

const formatTime = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  const now = new Date();
  const diffMinutes = Math.floor((now - date) / (1000 * 60));
  return diffMinutes < 60
    ? `${diffMinutes}分钟前`
    : `${Math.floor(diffMinutes / 60)}小时前`;
};

const getTooltipContent = (point) => {
  if (!point) return "";
  return `${formatTime(point.timestamp)}
      状态: ${point.status === "success" ? "正常" : "异常"}
      延迟: ${point.latency?.toFixed(2) ?? 0}ms
      ${point.error_message ? `错误: ${point.error_message}` : ""}`;
};

const validateHealthData = (data) => {
  if (!data || typeof data !== "object") return false;
  if (data.enabled === false) return true; // 添加对禁用状态的验证
  if (!Array.isArray(data.models)) return false;
  return data.models.every(
    (model) =>
      model.model_name &&
      Array.isArray(model.trend) &&
      typeof model.success_rate === "number" &&
      typeof model.avg_latency === "number" &&
      typeof model.current_latency === "number"
  );
};

const fetchHealthData = async () => {
  try {
    loading.value = true;
    error.value = null;

    const data = await request("/api/models/health/trend");
    console.log("Fetched data:", data);

    if (!validateHealthData(data)) {
      throw new Error("Invalid data format received");
    }

    healthData.value = data;
  } catch (err) {
    console.error("Error fetching health data:", err);
    if (err.response?.status !== 401) {
      error.value = err.message || "Failed to fetch health data";
    }
    healthData.value = null;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchHealthData();
  refreshInterval = setInterval(fetchHealthData, 5 * 60 * 1000);
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>

<style scoped>
.model-status-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
}

@media (min-width: 640px) {
  .model-status-container {
    padding: 24px;
  }
}

.shrug-icon {
  font-family: monospace;
  color: #666;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
}

.loading-state,
.error-state {
  min-height: 200px;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.error-state {
  color: #ff4d4f;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  color: white;
  background-color: #ff4d4f;
  white-space: nowrap;
}

.status-badge.success {
  background-color: #52c41a;
}

.status-timeline {
  margin: 1rem 0;
  height: 40px;
  margin-bottom: 2rem;
}

.timeline-info {
  display: flex;
  justify-content: space-between;
  color: #666;
  font-size: 0.75rem;
  margin-bottom: 0.25rem;
}

.status-bars {
  display: flex;
  gap: 1px;
  height: 100%;
  align-items: flex-end;
}

.status-bar-wrapper {
  flex: 1;
  height: 100%;
  position: relative;
}

.status-bar {
  width: 100%;
  position: absolute;
  bottom: 0;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.status-bar.healthy {
  background-color: #52c41a;
}

.status-bar.error {
  background-color: #ff4d4f;
}

.status-bar:hover {
  opacity: 0.8;
}

.status-bar:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 8px;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  font-size: 12px;
  border-radius: 4px;
  white-space: pre-line;
  z-index: 1000;
  margin-bottom: 4px;
  width: max-content;
  max-width: 200px;
  word-break: break-word;
}
</style>
