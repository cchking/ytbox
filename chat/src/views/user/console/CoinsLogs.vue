<template>
  <div class="h-full bg-white">
    <div
      class="relative flex flex-col h-full"
      @touchstart="handleTouchStart"
      @touchend="handleTouchEnd"
    >
      <div class="flex-1 p-4 sm:p-6 space-y-6 sm:space-y-8 overflow-auto">
        <!-- 统计卡片网格 -->
        <div
          class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 sm:gap-6"
        >
          <div
            v-for="card in statsCards"
            :key="card.key"
            class="relative overflow-hidden rounded-xl sm:rounded-2xl shadow-lg transition-all duration-300 hover:scale-105 hover:rotate-1"
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
                  <div
                    :class="[
                      'text-xl sm:text-2xl font-bold',
                      stats[card.key] > 0
                        ? 'text-green-600'
                        : stats[card.key] < 0
                        ? 'text-red-600'
                        : 'text-gray-800',
                    ]"
                  >
                    {{ stats[card.key] > 0 ? "+" : "" }}{{ stats[card.key] }}
                  </div>
                </div>
              </div>
            </div>
            <div
              class="absolute -right-4 -bottom-4 w-20 h-20 sm:w-24 sm:h-24 opacity-10"
              :style="{
                backgroundImage:
                  'radial-gradient(circle, currentColor 30%, transparent 70%)',
                color: card.color.includes('green')
                  ? '#059669'
                  : card.color.includes('red')
                  ? '#DC2626'
                  : card.color.includes('blue')
                  ? '#3B82F6'
                  : card.color.includes('yellow')
                  ? '#F59E0B'
                  : '#4B5563',
              }"
            />
          </div>
        </div>

        <!-- 筛选面板 -->
        <div class="bg-white rounded-xl sm:rounded-2xl shadow p-4 sm:p-6">
          <div
            class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-center"
          >
            <ElSelect
              v-model="filters.type"
              placeholder="选择类型"
              clearable
              class="!w-full sm:!w-40"
            >
              <ElOption
                v-for="option in typeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </ElSelect>

            <div class="grid grid-cols-2 sm:flex gap-3">
              <ElDatePicker
                v-model="filters.startDate"
                :type="datePickerType"
                placeholder="开始时间"
                clearable
                class="!w-full"
              />
              <ElDatePicker
                v-model="filters.endDate"
                :type="datePickerType"
                placeholder="结束时间"
                clearable
                class="!w-full"
              />
            </div>

            <div class="flex gap-3 sm:ml-auto">
              <button
                class="flex-1 sm:flex-none px-4 sm:px-6 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-all duration-200 transform hover:scale-105 active:scale-95"
                @click="handleFilter"
              >
                筛选
              </button>
              <button
                class="flex-1 sm:flex-none px-4 sm:px-6 py-2 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-all duration-200 transform hover:scale-105 active:scale-95"
                @click="resetFilter"
              >
                重置
              </button>
            </div>
          </div>
        </div>

        <!-- 记录展示区域 -->
        <div
          class="bg-white rounded-xl sm:rounded-2xl shadow-lg overflow-hidden"
        >
          <div class="relative flex flex-col min-h-[500px]">
            <!-- 加载动画 -->
            <div
              v-if="loading"
              class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10 transition-opacity duration-300"
            >
              <div
                class="w-12 h-12 sm:w-16 sm:h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"
              />
            </div>

            <!-- 桌面端表格 -->
            <div class="hidden sm:block flex-1 overflow-auto">
              <table class="w-full divide-y divide-gray-200">
                <thead class="bg-gray-50 sticky top-0 z-10">
                  <tr>
                    <th
                      v-for="header in ['时间', '类型', '金币变动', '说明']"
                      :key="header"
                      class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"
                    >
                      {{ header }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr
                    v-for="log in coinLogs"
                    :key="log.id"
                    class="hover:bg-gray-50 transition-all duration-150"
                  >
                    <td
                      class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                    >
                      {{ formatDate(log.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span :class="getTypeTagClass(log.type)">
                        {{ getTypeText(log.type) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        class="text-sm font-medium"
                        :class="getAmountClass(log.amount)"
                      >
                        {{ formatAmount(log.amount) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-500">
                      {{ log.description }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 移动端卡片列表 -->
            <div class="block sm:hidden flex-1 overflow-auto">
              <div class="space-y-3 p-4">
                <div
                  v-for="log in coinLogs"
                  :key="log.id"
                  class="bg-white rounded-lg shadow p-4 space-y-2 transform transition-all duration-200 hover:scale-102 active:scale-98"
                >
                  <div class="flex justify-between items-start">
                    <span
                      :class="getTypeTagClass(log.type)"
                      class="tag-animate"
                    >
                      {{ getTypeText(log.type) }}
                    </span>
                    <span
                      class="text-sm font-medium"
                      :class="getAmountClass(log.amount)"
                    >
                      {{ formatAmount(log.amount) }}
                    </span>
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ formatDate(log.created_at) }}
                  </div>
                  <div class="text-sm text-gray-700 break-words">
                    {{ log.description }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 分页器 -->
            <div
              class="mt-auto px-4 sm:px-6 py-4 bg-gray-50 border-t border-gray-200"
            >
              <div
                class="flex flex-col sm:flex-row items-center justify-between gap-4"
              >
                <span class="text-sm text-gray-700"
                  >共 {{ totalRecords }} 条记录</span
                >

                <div
                  class="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto"
                >
                  <select
                    v-model="pagination.pageSize"
                    class="w-full sm:w-auto border border-gray-300 rounded-full px-4 py-2 text-sm hover:border-blue-500 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 input-focus"
                    @change="handleSizeChange($event.target.value)"
                  >
                    <option value="10">10条/页</option>
                    <option value="20">20条/页</option>
                    <option value="50">50条/页</option>
                    <option value="100">100条/页</option>
                  </select>

                  <div
                    class="flex items-center gap-2 w-full sm:w-auto justify-center"
                  >
                    <button
                      class="page-btn px-4 py-2 rounded-full border border-gray-300 text-sm hover:bg-gray-100 transition-all duration-200 disabled:opacity-50 flex-1 sm:flex-none"
                      :disabled="pagination.currentPage === 1"
                      @click="handlePageChange(pagination.currentPage - 1)"
                    >
                      上一页
                    </button>
                    <span class="text-sm text-gray-700 whitespace-nowrap">
                      第 {{ pagination.currentPage }} 页
                    </span>
                    <button
                      class="page-btn px-4 py-2 rounded-full border border-gray-300 text-sm hover:bg-gray-100 transition-all duration-200 disabled:opacity-50 flex-1 sm:flex-none"
                      :disabled="
                        pagination.currentPage * pagination.pageSize >=
                        totalRecords
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
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import { ElMessage, ElDatePicker, ElSelect, ElOption } from "element-plus";
import {
  TrendingUp,
  TrendingDown,
  Settings,
  Award,
  Wallet,
} from "lucide-vue-next";
import { request } from "@/utils/request";

// 自定义 debounce 函数
const debounce = (fn, delay) => {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
};

export default {
  name: "CoinsLogs",
  components: {
    ElDatePicker,
    ElSelect,
    ElOption,
    TrendingUp,
    TrendingDown,
    Settings,
    Award,
    Wallet,
  },
  setup() {
    // 状态变量
    const stats = ref({
      currentBalance: 0,
      totalIncome: 0,
      totalExpense: 0,
      totalAdmin: 0,
      totalSignin: 0,
    });

    const coinLogs = ref([]);
    const loading = ref(false);
    const totalRecords = ref(0);
    const hoveredCard = ref(null);
    const datePickerType = ref(window.innerWidth < 640 ? "date" : "datetime");

    const pagination = ref({
      currentPage: 1,
      pageSize: 10,
    });

    const filters = ref({
      type: "",
      startDate: "",
      endDate: "",
    });

    // 类型选项
    const typeOptions = [
      { value: "income", label: "收入" },
      { value: "consume", label: "消费" },
      { value: "admin", label: "管理员操作" },
      { value: "signin", label: "签到奖励" },
    ];

    // 统计卡片配置
    const statsCards = [
      {
        title: "当前余额",
        key: "currentBalance",
        icon: Wallet,
        color: "bg-purple-500",
        bgColor: "bg-purple-50",
      },
      {
        title: "总收入",
        key: "totalIncome",
        icon: TrendingUp,
        color: "bg-green-500",
        bgColor: "bg-green-50",
      },
      {
        title: "总支出",
        key: "totalExpense",
        icon: TrendingDown,
        color: "bg-red-500",
        bgColor: "bg-red-50",
      },
      {
        title: "管理员操作",
        key: "totalAdmin",
        icon: Settings,
        color: "bg-blue-500",
        bgColor: "bg-blue-50",
      },
      {
        title: "签到奖励",
        key: "totalSignin",
        icon: Award,
        color: "bg-yellow-500",
        bgColor: "bg-yellow-50",
      },
    ];

    // 获取消费记录
    const fetchCoinLogs = async () => {
      loading.value = true;
      try {
        const params = new URLSearchParams({
          page: pagination.value.currentPage.toString(),
          page_size: pagination.value.pageSize.toString(),
        });

        if (filters.value.type) {
          params.append("type", filters.value.type);
        }
        if (filters.value.startDate) {
          params.append(
            "start_date",
            new Date(filters.value.startDate).toISOString()
          );
        }
        if (filters.value.endDate) {
          params.append(
            "end_date",
            new Date(filters.value.endDate).toISOString()
          );
        }

        const response = await request(
          `/api/user/coins/logs?${params.toString()}`
        );
        coinLogs.value = response.logs;
        totalRecords.value = response.total;
        Object.assign(stats.value, {
          totalIncome: response.total_income,
          totalExpense: response.total_expense,
          totalAdmin: response.total_admin,
          totalSignin: response.total_signin,
          currentBalance: response.current_balance,
        });
      } catch (error) {
        ElMessage.error({
          message: error.response?.data?.message || "获取消费记录失败",
          plain: true,
        });
        console.error("Error fetching coin logs:", error);
      } finally {
        loading.value = false;
      }
    };

    // 处理页码变化
    const handlePageChange = (newPage) => {
      pagination.value.currentPage = newPage;
      fetchCoinLogs();
    };

    // 处理每页数量变化
    const handleSizeChange = (newSize) => {
      pagination.value.pageSize = parseInt(newSize);
      pagination.value.currentPage = 1;
      fetchCoinLogs();
    };

    // 处理筛选 - 使用防抖
    const debouncedFilter = debounce(() => {
      pagination.value.currentPage = 1;
      fetchCoinLogs();
    }, 300);

    const handleFilter = () => {
      debouncedFilter();
    };

    // 重置筛选
    const resetFilter = () => {
      filters.value = {
        type: "",
        startDate: "",
        endDate: "",
      };
      handleFilter();
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

    // 获取类型标签样式
    const getTypeTagClass = (type) => {
      const baseClasses =
        "px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full transition-transform duration-200";
      switch (type) {
        case "consume":
          return `${baseClasses} bg-red-100 text-red-800`;
        case "income":
          return `${baseClasses} bg-green-100 text-green-800`;
        case "admin":
          return `${baseClasses} bg-yellow-100 text-yellow-800`;
        case "signin":
          return `${baseClasses} bg-blue-100 text-blue-800`;
        default:
          return `${baseClasses} bg-gray-100 text-gray-800`;
      }
    };

    // 获取类型文本
    const getTypeText = (type) => {
      const typeMap = {
        consume: "消费",
        income: "收入",
        admin: "管理员操作",
        signin: "签到奖励",
      };
      return typeMap[type] || type;
    };

    // 获取金额样式
    const getAmountClass = (amount) => {
      return amount > 0 ? "text-green-600" : "text-red-600";
    };

    // 格式化金额
    const formatAmount = (amount) => {
      return amount > 0 ? `+${amount}` : amount;
    };

    // 处理下拉刷新
    let touchStartY = 0;
    const handleTouchStart = (e) => {
      touchStartY = e.touches[0].clientY;
    };

    const handleTouchEnd = (e) => {
      const touchEndY = e.changedTouches[0].clientY;
      const diff = touchEndY - touchStartY;

      if (diff > 100 && window.scrollY === 0) {
        fetchCoinLogs();
      }
    };

    // 监听窗口大小变化
    const handleResize = () => {
      datePickerType.value = window.innerWidth < 640 ? "date" : "datetime";
    };

    onMounted(() => {
      fetchCoinLogs();
      window.addEventListener("resize", handleResize);
      document.addEventListener("touchstart", handleTouchStart);
      document.addEventListener("touchend", handleTouchEnd);
    });

    onUnmounted(() => {
      window.removeEventListener("resize", handleResize);
      document.removeEventListener("touchstart", handleTouchStart);
      document.removeEventListener("touchend", handleTouchEnd);
    });

    return {
      stats,
      coinLogs,
      loading,
      totalRecords,
      hoveredCard,
      datePickerType,
      pagination,
      filters,
      typeOptions,
      statsCards,
      handlePageChange,
      handleSizeChange,
      handleFilter,
      resetFilter,
      formatDate,
      getTypeTagClass,
      getTypeText,
      getAmountClass,
      formatAmount,
      handleTouchStart,
      handleTouchEnd,
    };
  },
};
</script>

<style>
/* 卡片悬浮动画 */
@keyframes float {
  0%,
  100% {
    transform: translateY(0) rotate(0);
  }
  50% {
    transform: translateY(-5px) rotate(1deg);
  }
}

.stats-card {
  animation: float 3s ease-in-out infinite;
}

/* 标签动画 */
@keyframes pop {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.tag-animate:hover {
  animation: pop 0.3s ease-in-out;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-select-dropdown) {
  @apply rounded-xl border border-gray-200 shadow-lg;
}

:deep(.el-select-dropdown__item) {
  @apply transition-colors duration-200;
}

:deep(.el-select-dropdown__item.hover),
:deep(.el-select-dropdown__item:hover) {
  @apply bg-blue-50;
}

:deep(.el-input__wrapper) {
  @apply !rounded-full;
}

:deep(.el-input__inner) {
  @apply !rounded-full;
}

:deep(.el-date-picker) {
  @apply rounded-xl border border-gray-200 shadow-lg;
}

:deep(.el-picker-panel) {
  @apply rounded-xl border border-gray-200 shadow-lg;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  @apply w-2;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded-full;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-300 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400;
}

/* 移动端优化 */
@media (max-width: 640px) {
  .stats-card {
    @apply p-4;
  }

  .text-2xl {
    @apply text-xl;
  }

  ::-webkit-scrollbar {
    @apply w-1;
  }

  .btn-hover {
    @apply text-sm py-1.5;
  }

  .loading-mask .animate-spin {
    @apply w-12 h-12;
  }
}

/* 触摸设备交互优化 */
@media (hover: none) {
  .btn-hover:hover {
    transform: none;
    box-shadow: none;
  }

  .table-row:hover {
    transform: none;
  }
}

/* 下拉刷新提示 */
.pull-to-refresh {
  @apply text-gray-500 text-sm text-center py-2;
}

/* 按钮触摸反馈 */
.touch-feedback {
  position: relative;
  overflow: hidden;
}

.touch-feedback::after {
  content: "";
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  background-image: radial-gradient(
    circle,
    rgba(0, 0, 0, 0.1) 10%,
    transparent 10.01%
  );
  background-repeat: no-repeat;
  background-position: 50%;
  transform: scale(10);
  opacity: 0;
  transition: transform 0.5s, opacity 1s;
}

.touch-feedback:active::after {
  transform: scale(0);
  opacity: 0.3;
  transition: 0s;
}

/* 优化移动端滚动 */
.overflow-auto {
  -webkit-overflow-scrolling: touch;
}

/* 修改表格容器样式 */
.table-container {
  position: relative;
  min-height: 500px;
  height: calc(100vh - 400px);
}

/* 固定底部分页器 */
.sticky {
  position: sticky;
  bottom: 0;
  background: white;
  z-index: 10;
  border-top: 1px solid #e5e7eb;
}

/* 优化移动端滚动 */
@media (max-width: 640px) {
  .table-container {
    height: auto;
    min-height: 300px;
  }
}
</style>
