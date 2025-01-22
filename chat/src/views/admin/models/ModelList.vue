<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <!-- Header Section -->
    <div class="max-w-7xl mx-auto">
      <div
        class="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0"
      >
        <div
          class="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-6"
        >
          <h1 class="text-2xl font-bold text-gray-900">模型管理</h1>
          <div class="inline-flex rounded-lg shadow-sm">
            <button
              @click="showDeletedModels = !showDeletedModels"
              class="relative inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              :class="[
                showDeletedModels
                  ? 'bg-purple-600 text-white hover:bg-purple-700'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300',
              ]"
            >
              <span class="flex items-center">
                <svg
                  :class="[
                    'w-4 h-4 mr-2',
                    showDeletedModels ? 'text-purple-200' : 'text-gray-400',
                  ]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                {{ showDeletedModels ? "查看正常模型" : "查看已删除" }}
              </span>
            </button>
          </div>
        </div>
        <div class="flex space-x-4 w-full sm:w-auto">
          <!-- Search Input -->
          <div class="relative flex-1 sm:flex-none sm:min-w-[300px]">
            <input
              v-model="searchQuery"
              type="text"
              class="w-full px-4 py-2 pl-10 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
              placeholder="搜索模型名称、公司或标签..."
            />
            <div
              class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
            >
              <svg
                class="h-5 w-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>
          <!-- Add Model Button -->
          <button
            @click="openCreateModal"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
          >
            <svg
              class="w-4 h-4 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            添加模型
          </button>
        </div>
      </div>

      <!-- Model Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="model in filteredModels"
          :key="model.id"
          class="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden"
          :class="{ 'ring-2 ring-red-200': model.is_deleted }"
        >
          <div class="p-6">
            <!-- Model Header -->
            <div class="flex items-start space-x-4">
              <div
                class="h-12 w-12 rounded-lg flex items-center justify-center flex-shrink-0"
                :class="[
                  model.icon
                    ? 'bg-transparent'
                    : 'bg-gradient-to-br from-blue-500 to-purple-600',
                ]"
              >
                <img
                  v-if="model.icon"
                  :src="model.icon"
                  class="h-12 w-12 rounded-lg object-cover"
                  :alt="model.name"
                />
                <svg
                  v-else
                  class="h-6 w-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <h3 class="text-lg font-semibold text-gray-900 truncate">
                    {{ model.name }}
                  </h3>
                  <div class="flex items-center space-x-2">
                    <span
                      :class="[
                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                        model.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800',
                      ]"
                    >
                      {{ model.is_active ? "启用" : "禁用" }}
                    </span>
                    <span
                      v-if="model.is_deleted"
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                    >
                      已删除
                    </span>
                  </div>
                </div>
                <p class="mt-1 text-sm text-gray-500">{{ model.company }}</p>
              </div>
            </div>

            <!-- Tags -->
            <div class="mt-4 flex flex-wrap gap-2">
              <span
                v-for="tag in getTags(model.tags)"
                :key="tag"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100"
              >
                {{ tag }}
              </span>
            </div>

            <!-- Description -->
            <p class="mt-4 text-sm text-gray-600 line-clamp-2">
              {{ model.description || "暂无描述" }}
            </p>

            <!-- Group Badge -->
            <div class="mt-4">
              <span
                :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  getGroupClass(model.group),
                ]"
              >
                {{ getGroupText(model) }}
              </span>
            </div>

            <!-- Actions -->
            <div class="mt-6 flex justify-end space-x-2">
              <button
                v-if="!model.is_deleted"
                @click="() => openEditModal(model)"
                class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors duration-200"
              >
                <svg
                  class="w-4 h-4 mr-1.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
                编辑
              </button>
              <button
                v-if="!model.is_deleted"
                @click="() => toggleModelStatus(model.id)"
                :class="[
                  'inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium transition-colors duration-200',
                  model.is_active
                    ? 'text-red-700 bg-red-50 hover:bg-red-100'
                    : 'text-green-700 bg-green-50 hover:bg-green-100',
                ]"
              >
                <svg
                  class="w-4 h-4 mr-1.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    v-if="model.is_active"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
                  />
                  <path
                    v-else
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                {{ model.is_active ? "禁用" : "启用" }}
              </button>
              <button
                v-if="!model.is_deleted"
                @click="() => handleDelete(model)"
                class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium text-red-700 bg-red-50 hover:bg-red-100 transition-colors duration-200"
              >
                <svg
                  class="w-4 h-4 mr-1.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                删除
              </button>
              <button
                v-if="model.is_deleted"
                @click="() => handleRestore(model)"
                class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium text-green-700 bg-green-50 hover:bg-green-100 transition-colors duration-200"
              >
                <svg
                  class="w-4 h-4 mr-1.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                恢复
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="filteredModels.length === 0"
        class="mt-8 text-center py-12 bg-white rounded-xl shadow-sm"
      >
        <div
          class="rounded-full bg-gray-100 w-16 h-16 flex items-center justify-center mx-auto"
        >
          <svg
            class="h-8 w-8 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
        </div>
        <h3 class="mt-4 text-lg font-medium text-gray-900">
          {{
            searchQuery
              ? "未找到匹配的模型"
              : showDeletedModels
              ? "暂无已删除模型"
              : "暂无模型"
          }}
        </h3>
        <p class="mt-2 text-sm text-gray-500 max-w-sm mx-auto">
          {{
            searchQuery
              ? "请尝试使用其他搜索关键词"
              : showDeletedModels
              ? "所有模型都在正常使用中"
              : "开始添加一个新的模型来管理您的服务"
          }}
        </p>
        <div v-if="!showDeletedModels && !searchQuery" class="mt-6">
          <button
            @click="openCreateModal"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
          >
            <svg
              class="w-4 h-4 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            添加模型
          </button>
        </div>
      </div>
    </div>

    <!-- Model Form Modal -->
    <ModelForm
      v-if="showCreateModal || showEditModal"
      :model="selectedModel"
      :is-edit="!!selectedModel"
      @close="closeModelModal"
      @submit="handleModelSubmit"
    />

    <!-- Error Toast -->
    <div
      v-if="error"
      class="fixed bottom-4 right-4 max-w-md bg-white border-l-4 border-red-500 rounded-lg shadow-lg transform transition-all duration-300 ease-in-out"
    >
      <div class="p-4 flex items-start">
        <div class="flex-shrink-0">
          <svg
            class="h-5 w-5 text-red-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="ml-3 w-0 flex-1">
          <p class="text-sm text-gray-900">{{ error }}</p>
        </div>
        <div class="ml-4 flex-shrink-0 flex">
          <button
            @click="error = ''"
            class="inline-flex text-gray-400 hover:text-gray-500 focus:outline-none"
          >
            <svg
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { request } from "@/utils/request";
import ModelForm from "./ModelForm.vue";

const models = ref([]);
const deletedModels = ref([]);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const selectedModel = ref(null);
const error = ref("");
const showDeletedModels = ref(false);
const searchQuery = ref("");

// 获取分组样式
const getGroupClass = (group) => {
  switch (group) {
    case "vip":
      return "bg-purple-100 text-purple-800";
    case "coin":
      return "bg-amber-100 text-amber-800";
    case "free":
      return "bg-green-100 text-green-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
};

// 获取分组文本
const getGroupText = (model) => {
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
};

// 搜索过滤后的模型列表
const filteredModels = computed(() => {
  const currentModels = showDeletedModels.value
    ? deletedModels.value
    : models.value;
  if (!searchQuery.value) return currentModels;

  const query = searchQuery.value.toLowerCase();
  return currentModels.filter((model) => {
    const name = (model.name || "").toLowerCase();
    const company = (model.company || "").toLowerCase();
    const tags = (model.tags || "").toLowerCase();
    const description = (model.description || "").toLowerCase();

    return (
      name.includes(query) ||
      company.includes(query) ||
      tags.includes(query) ||
      description.includes(query)
    );
  });
});

const fetchModels = async () => {
  try {
    const response = await request("/api/admin/channel-models", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    models.value = response;
  } catch (error) {
    console.error("Failed to fetch models:", error);
    showError(error);
  }
};

const fetchDeletedModels = async () => {
  try {
    const response = await request("/api/admin/models-trash", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    deletedModels.value = response;
  } catch (error) {
    console.error("Failed to fetch deleted models:", error);
    showError(error);
  }
};

const getTags = (tags) => {
  if (!tags) return [];
  return tags.split(",").filter(Boolean);
};

const openCreateModal = () => {
  selectedModel.value = null;
  showCreateModal.value = true;
};

const openEditModal = (model) => {
  selectedModel.value = { ...model };
  showEditModal.value = true;
};

const closeModelModal = () => {
  showCreateModal.value = false;
  showEditModal.value = false;
  selectedModel.value = null;
};

const showError = (error) => {
  if (error.status === 403) {
    error.value = "您没有权限执行此操作";
  } else {
    error.value = error.message || "操作失败";
  }
  setTimeout(() => {
    error.value = "";
  }, 3000);
};

const handleModelSubmit = async (modelData) => {
  try {
    await fetchModels();
    closeModelModal();
  } catch (err) {
    console.error("Failed to handle model submission:", err);
    showError(err);
  }
};

const toggleModelStatus = async (modelId) => {
  try {
    await request(`/api/admin/models/${modelId}/toggle`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
    });
    await fetchModels();
  } catch (error) {
    console.error("Failed to toggle model status:", error);
    showError(error);
  }
};

const handleDelete = async (model) => {
  if (!confirm(`确定要删除模型 "${model.name}" 吗？`)) return;

  try {
    await request(`/api/admin/models/${model.id}/delete`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    await fetchModels();
    await fetchDeletedModels();
  } catch (error) {
    console.error("Failed to delete model:", error);
    showError(error);
  }
};

const handleRestore = async (model) => {
  if (!confirm(`确定要恢复模型 "${model.name}" 吗？`)) return;

  try {
    await request(`/api/admin/models/${model.id}/restore`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    await fetchModels();
    await fetchDeletedModels();
  } catch (error) {
    console.error("Failed to restore model:", error);
    showError(error);
  }
};

watch(showDeletedModels, (newVal) => {
  if (newVal) {
    fetchDeletedModels();
  }
});

onMounted(async () => {
  await fetchModels();
  if (showDeletedModels.value) {
    await fetchDeletedModels();
  }
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
