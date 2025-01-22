<template>
  <div class="flex justify-center items-center h-full">
    <div class="inline-block">
      <!-- 加载状态显示 -->
      <div v-if="loading" class="flex items-center space-x-2 p-2">
        <div class="animate-pulse w-8 h-8 bg-gray-200 rounded-full"></div>
        <div class="animate-pulse w-24 h-4 bg-gray-200 rounded"></div>
      </div>

      <!-- 加载完成状态 -->
      <template v-else>
        <button
          @click="toggleSelector"
          class="inline-flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100"
        >
          <div class="w-8 h-8 relative">
            <img
              v-if="currentModel?.icon"
              :src="currentModel.icon"
              class="w-full h-full object-cover rounded"
              :alt="getModelDisplayName(currentModel)"
              @error="handleImageError"
            />
            <div
              v-else
              class="w-full h-full flex items-center justify-center bg-gray-200 rounded"
            >
              {{ getModelFirstChar(currentModel) }}
            </div>
          </div>
          <div class="flex items-center justify-center mx-2">
            {{ getModelDisplayName(currentModel) }}
          </div>
          <svg
            class="w-4 h-4 transition-transform"
            :class="{ 'rotate-180': showSelector }"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        <!-- 下拉选择框 -->
        <div
          v-if="showSelector"
          :class="[
            'bg-white rounded-lg shadow-xl divide-y divide-gray-100 z-50 w-80',
            isMobile ? 'fixed top-16 right-4' : 'absolute top-full left-2 mt-2',
          ]"
        >
          <!-- 分类和搜索栏 -->
          <div class="p-2 space-y-2">
            <!-- 分类选项卡 -->
            <div class="flex space-x-2">
              <button
                v-for="tab in tabs"
                :key="tab.value"
                @click="currentTab = tab.value"
                class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
                :class="[
                  currentTab === tab.value
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100',
                ]"
              >
                {{ tab.label }}
              </button>
            </div>
            <!-- 搜索框 -->
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="`搜索${getCurrentTabLabel()}...`"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <!-- 模型列表 -->
          <div class="max-h-96 overflow-y-auto">
            <template v-if="filteredModels.length">
              <div
                v-for="model in filteredModels"
                :key="model.id"
                @click="selectModel(model)"
                class="flex items-center p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                :class="{ 'bg-blue-50': currentModel?.id === model.id }"
              >
                <div class="w-8 h-8 relative mr-3">
                  <img
                    v-if="model.icon"
                    :src="model.icon"
                    class="w-full h-full object-cover rounded"
                    :alt="getModelDisplayName(model)"
                    @error="handleImageError"
                  />
                  <div
                    v-else
                    class="w-full h-full flex items-center justify-center bg-gray-200 rounded text-sm"
                  >
                    {{ getModelFirstChar(model) }}
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="font-medium truncate">
                    {{ getModelDisplayName(model) }}
                  </div>
                  <div class="text-sm text-gray-500 truncate">
                    {{ model.description || "暂无描述" }}
                  </div>
                </div>
                <div class="ml-2 flex-shrink-0">
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      getModelTypeClass(model),
                    ]"
                  >
                    {{ getModelTypeText(model) }}
                  </span>
                </div>
              </div>
            </template>
            <div v-else class="p-4 text-center text-sm text-gray-500">
              未找到匹配的模型
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { request } from "@/utils/request";

// Props
const props = defineProps({
  initialModelId: {
    type: String,
    default: null,
  },
});

// Emits
const emit = defineEmits(["select", "error"]);

// State
const loading = ref(true);
const systemModels = ref([]);
const marketModels = ref([]);
const privateModels = ref([]);
const currentModel = ref(null);
const showSelector = ref(false);
const searchQuery = ref("");
const currentTab = ref("system");
const isMobile = ref(window.innerWidth < 640);

// 定义选项卡
const tabs = [
  { label: "系统模型", value: "system" },
  { label: "模型市场", value: "market" },
  { label: "私人模型", value: "private" },
];

// 获取当前选项卡标签
const getCurrentTabLabel = () => {
  const tab = tabs.find((t) => t.value === currentTab.value);
  return tab ? tab.label : "";
};

// 获取模型显示名称
const getModelDisplayName = (model) => {
  if (!model) return "选择模型";

  // 对于市场模型和私人模型使用完整id
  if (currentTab.value === "market" || currentTab.value === "private") {
    return String(model.id || "");
  }

  // 系统模型使用name
  return String(model.name || model.id || "");
};

// 获取模型首字符
const getModelFirstChar = (model) => {
  if (!model) return "?";
  const name = String(model.name || model.id || "");
  return name.charAt(0) || "?";
};

// 获取模型类型样式
const getModelTypeClass = (model) => {
  if (currentTab.value === "system") {
    switch (model.group) {
      case "vip":
        return "bg-purple-100 text-purple-800";
      case "coin":
        return "bg-amber-100 text-amber-800";
      case "free":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  } else if (currentTab.value === "market") {
    return model.usage_type === "free"
      ? "bg-green-100 text-green-800"
      : "bg-amber-100 text-amber-800";
  } else {
    return "bg-gray-100 text-gray-800";
  }
};

// 获取模型类型文本
const getModelTypeText = (model) => {
  if (currentTab.value === "system") {
    switch (model.group) {
      case "vip":
        return "VIP";
      case "coin":
        return `${model.price?.price || 0} 金币`;
      case "free":
        return "免费";
      default:
        return "未知";
    }
  } else if (currentTab.value === "market") {
    if (model.usage_type === "free") {
      return "免费";
    } else if (model.usage_type === "coin") {
      return `${model.usage_price} 金币`;
    }
    return "未知";
  } else {
    return "私人";
  }
};

// 计算当前显示的模型列表
const currentModels = computed(() => {
  switch (currentTab.value) {
    case "system":
      return systemModels.value;
    case "market":
      return marketModels.value;
    case "private":
      return privateModels.value;
    default:
      return [];
  }
});

// 计算属性：过滤模型
const filteredModels = computed(() => {
  const query = searchQuery.value.toLowerCase().trim();
  const models = currentModels.value;

  if (!query) return models;

  return models.filter((model) => {
    const searchText = String(model.name || model.id || "").toLowerCase();
    return (
      searchText.includes(query) ||
      model.description?.toLowerCase().includes(query)
    );
  });
});

// 方法
const fetchSystemModels = async () => {
  try {
    const data = await request("/api/models");
    systemModels.value = data.filter(
      (model) => !model.is_deleted && model.name
    );
  } catch (error) {
    console.error("Failed to fetch system models:", error);
    emit("error", error);
  }
};

const fetchMarketModels = async () => {
  try {
    const { items } = await request("/api/user/available-models?type=pulled");
    marketModels.value = items;
  } catch (error) {
    console.error("Failed to fetch market models:", error);
    emit("error", error);
  }
};

const fetchPrivateModels = async () => {
  try {
    const { items } = await request("/api/user/available-models?type=private");
    privateModels.value = items;
  } catch (error) {
    console.error("Failed to fetch private models:", error);
    emit("error", error);
  }
};

// 加载所有模型
const fetchAllModels = async () => {
  try {
    loading.value = true;
    await Promise.all([
      fetchSystemModels(),
      fetchMarketModels(),
      fetchPrivateModels(),
    ]);

    // 设置初始模型
    if (props.initialModelId) {
      const allModels = [
        ...systemModels.value,
        ...marketModels.value,
        ...privateModels.value,
      ];
      currentModel.value = allModels.find((m) => m.id === props.initialModelId);
    } else if (systemModels.value.length > 0) {
      currentModel.value = systemModels.value[0];
    }

    if (currentModel.value) {
      emit("select", currentModel.value);
    }
  } catch (error) {
    console.error("Failed to fetch models:", error);
    emit("error", error);
  } finally {
    loading.value = false;
  }
};

const selectModel = (model) => {
  console.log("模型选择时的原始数据:", model);
  currentModel.value = model;

  const modelData = {
    ...model,
    model: model.id,
  };
  console.log("准备发送给父组件的模型数据:", modelData);

  localStorage.setItem("selectedModel", JSON.stringify(modelData));
  emit("select", modelData);
  closeSelector();
};

const toggleSelector = () => {
  showSelector.value = !showSelector.value;
};

const closeSelector = () => {
  showSelector.value = false;
};

const handleImageError = (event) => {
  event.target.style.display = "none";
  const placeholder = event.target.nextElementSibling;
  if (placeholder) {
    placeholder.style.display = "flex";
  }
};

const handleResize = () => {
  isMobile.value = window.innerWidth < 640;
};

// 点击外部关闭下拉框
const handleClickOutside = (event) => {
  const container = event.target.closest(".inline-block");
  if (!container) {
    closeSelector();
  }
};

// 当切换选项卡时重置搜索
watch(currentTab, () => {
  searchQuery.value = "";
});

// 生命周期钩子
onMounted(() => {
  fetchAllModels();
  document.addEventListener("click", handleClickOutside);
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
  window.removeEventListener("resize", handleResize);
});
</script>
