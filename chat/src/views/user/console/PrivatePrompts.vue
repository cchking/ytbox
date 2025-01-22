<!-- src/views/PrivatePrompts.vue -->
<template>
  <div class="min-h-screen bg-white">
    <!-- 头部区域 -->
    <div class="max-w-7xl mx-auto pt-6 pb-8 px-4">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">私有提示词</h1>
          <p class="mt-1 text-sm text-gray-500">
            管理您的个人提示词模板，可一键发布到市场
          </p>
        </div>
        <button
          @click="openCreateDialog()"
          class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-sm transition-all duration-150 ease-in-out"
        >
          <PlusIcon class="h-5 w-5 mr-2" />
          新建提示词
        </button>
      </div>
    </div>

    <!-- 提示词列表 -->
    <div class="max-w-7xl mx-auto px-4">
      <div
        v-if="prompts.length === 0"
        class="text-center py-12 bg-white rounded-xl shadow-sm"
      >
        <FileIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">暂无提示词</h3>
        <p class="mt-1 text-sm text-gray-500">开始创建您的第一个提示词模板</p>
        <div class="mt-6">
          <button
            @click="openCreateDialog()"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon class="h-5 w-5 mr-2" />
            新建提示词
          </button>
        </div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="prompt in prompts"
          :key="prompt.id"
          class="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden border border-gray-100"
        >
          <div class="p-6">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 line-clamp-1">
                  {{ prompt.title }}
                </h3>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="openEditDialog(prompt)"
                  class="text-gray-400 hover:text-blue-600 transition-colors duration-150"
                  title="编辑"
                >
                  <PencilIcon class="h-5 w-5" />
                </button>
                <button
                  @click="openPublishDialog(prompt)"
                  class="text-gray-400 hover:text-amber-600 transition-colors duration-150"
                  title="发布"
                >
                  <ShareIcon class="h-5 w-5" />
                </button>
                <button
                  @click="deletePrompt(prompt.id)"
                  class="text-gray-400 hover:text-red-600 transition-colors duration-150"
                  title="删除"
                >
                  <TrashIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
            <p class="mt-3 text-sm text-gray-500 line-clamp-2">
              {{ prompt.description }}
            </p>
            <div class="mt-4 flex items-center text-xs text-gray-500">
              <ClockIcon class="h-4 w-4 mr-1" />
              {{ new Date(prompt.created_at).toLocaleString() }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 发布对话框 -->
    <div
      v-if="showPublishDialog"
      class="fixed inset-0 bg-black bg-opacity-50 transition-opacity flex items-center justify-center p-4 z-50"
      @click.self="showPublishDialog = false"
    >
      <div
        class="bg-white rounded-xl shadow-xl w-full max-w-md transform transition-all"
      >
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-gray-900">发布到市场</h2>
            <button
              @click="showPublishDialog = false"
              class="text-gray-400 hover:text-gray-500"
            >
              <XIcon class="h-6 w-6" />
            </button>
          </div>
          <form @submit.prevent="handlePublish" class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >价格</label
              >
              <input
                v-model="publishForm.price"
                type="number"
                min="0"
                class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm py-2"
                required
              />
            </div>
            <!-- 标签选择器 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >标签</label
              >
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="tag in availableTags"
                  :key="tag.id"
                  type="button"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm transition-colors"
                  :class="[
                    publishForm.tags.includes(tag.id)
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
                  ]"
                  @click="toggleTag(tag.id)"
                >
                  {{ tag.name }}
                </button>
              </div>
            </div>
            <div class="flex justify-end gap-3">
              <button
                type="button"
                @click="showPublishDialog = false"
                class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                取消
              </button>
              <button
                type="submit"
                class="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                发布
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 在 showPublishDialog 对话框后添加以下代码 -->

    <!-- 创建/编辑对话框 -->
    <div
      v-if="showDialog"
      class="fixed inset-0 bg-black bg-opacity-50 transition-opacity flex items-center justify-center p-4 z-50"
      @click.self="showDialog = false"
    >
      <div
        class="bg-white rounded-xl shadow-xl w-full max-w-lg transform transition-all"
      >
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-gray-900">
              {{ isEditing ? "编辑提示词" : "创建提示词" }}
            </h2>
            <button
              @click="showDialog = false"
              class="text-gray-400 hover:text-gray-500"
            >
              <XIcon class="h-6 w-6" />
            </button>
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-6">
            <!-- 标题 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                标题 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.title"
                type="text"
                required
                placeholder="输入标题"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base md:text-sm"
              />
            </div>

            <!-- 描述 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                描述 <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="formData.description"
                required
                rows="3"
                placeholder="输入描述"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base md:text-sm"
              ></textarea>
            </div>

            <!-- 提示词内容 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                提示词内容 <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="formData.content"
                required
                rows="6"
                placeholder="输入提示词内容"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-base md:text-sm"
              ></textarea>
            </div>

            <!-- 操作按钮 -->
            <div class="flex justify-end gap-3 mt-6">
              <button
                type="button"
                @click="showDialog = false"
                class="px-4 py-2 border border-gray-300 rounded-lg text-base md:text-sm font-medium text-gray-700 hover:bg-gray-50 h-10 md:h-9"
              >
                取消
              </button>
              <button
                type="submit"
                class="px-4 py-2 border border-transparent rounded-lg shadow-sm text-base md:text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 h-10 md:h-9"
              >
                {{ isEditing ? "保存" : "创建" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <!-- ... -->
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { request } from "@/utils/request";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ClockIcon,
  ShareIcon,
  XIcon,
  FileIcon,
} from "lucide-vue-next";

// 数据相关
const prompts = ref([]);
const showDialog = ref(false);
const showPublishDialog = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const availableTags = ref([]); // 存储可用标签列表

const formData = ref({
  title: "",
  description: "",
  content: "",
});

const publishForm = ref({
  price: 0,
  tags: [], // 改为存储标签ID数组
});

// 初始化
onMounted(async () => {
  await Promise.all([fetchPrompts(), fetchTags()]);
});

// 获取标签列表
const fetchTags = async () => {
  try {
    const data = await request("/api/admin/tags");
    availableTags.value = data;
  } catch (error) {
    ElMessage.error({
      message: "获取标签列表失败",
      plain: true,
    });
  }
};

// 切换标签选择状态
const toggleTag = (tagId) => {
  const index = publishForm.value.tags.indexOf(tagId);
  if (index === -1) {
    publishForm.value.tags.push(tagId);
  } else {
    publishForm.value.tags.splice(index, 1);
  }
};

// Methods...
const fetchPrompts = async () => {
  try {
    const data = await request("/api/private-prompts");
    prompts.value = data;
  } catch (error) {
    ElMessage.error({
      message: "获取提示词列表失败",
      plain: true,
    });
  }
};

const openCreateDialog = () => {
  isEditing.value = false;
  currentId.value = null;
  formData.value = {
    title: "",
    description: "",
    content: "",
  };
  showDialog.value = true;
};

const openEditDialog = (prompt) => {
  isEditing.value = true;
  currentId.value = prompt.id;
  formData.value = {
    title: prompt.title,
    description: prompt.description,
    content: prompt.content,
  };
  showDialog.value = true;
};

// 打开发布对话框时确保正确设置 currentId
const openPublishDialog = (prompt) => {
  console.log("Opening publish dialog for prompt:", prompt); // 添加日志
  currentId.value = prompt.id;
  console.log("Set currentId.value to:", currentId.value); // 添加日志
  publishForm.value = {
    price: 0,
    tags: [],
  };
  showPublishDialog.value = true;
};

// 处理发布请求
const handlePublish = async () => {
  console.log("Handling publish for prompt id:", currentId.value); // 添加日志
  try {
    const response = await request(
      `/api/private-prompts/${currentId.value}/publish`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt_id: currentId.value, // 确保包含 prompt_id
          price: publishForm.value.price,
          tags: publishForm.value.tags,
        }),
      }
    );

    console.log("Publish response:", response); // 添加日志

    ElMessage.success({
      message: "发布成功",
      plain: true,
    });
    showPublishDialog.value = false;
    await fetchPrompts();
  } catch (error) {
    console.error("Publish error:", error); // 添加错误日志
    if (error.response) {
      const errorData = await error.response.json();
      ElMessage.error({
        message: errorData.detail?.[0]?.msg || "发布失败",
        plain: true,
      });
    } else {
      ElMessage.error({
        message: "发布失败",
        plain: true,
      });
    }
  }
};
const handleSubmit = async () => {
  try {
    if (isEditing.value) {
      await request(`/api/private-prompts/${currentId.value}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData.value),
      });
      ElMessage.success({
        message: "更新提示词成功",
        plain: true,
      });
    } else {
      await request("/api/private-prompts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData.value),
      });
      ElMessage.success({
        message: "创建提示词成功",
        plain: true,
      });
    }
    showDialog.value = false;
    await fetchPrompts();
  } catch (error) {
    ElMessage.error({
      message: isEditing.value ? "更新提示词失败" : "创建提示词失败",
      plain: true,
    });
  }
};

const deletePrompt = async (id) => {
  try {
    const confirmed = await ElMessageBox.confirm(
      "删除后将无法恢复，是否确认删除？",
      "警告",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    if (confirmed === "confirm") {
      await request(`/api/private-prompts/${id}`, {
        method: "DELETE",
      });
      ElMessage.success({
        message: "删除提示词成功",
        plain: true,
      });
      await fetchPrompts();
    }
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error({
        message: "删除提示词失败",
        plain: true,
      });
    }
  }
};
</script>

<style scoped>
/* 文本省略 */
.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 卡片悬浮效果 */
.prompt-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

/* 输入框焦点状态 */
input:focus,
textarea:focus,
select:focus {
  outline: none;
  ring-color: rgb(59 130 246);
  ring-offset-width: 2px;
  ring-offset-color: #fff;
}

/* 按钮动画 */
button {
  transition: all 0.2s ease;
}

button:active {
  transform: scale(0.98);
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}

/* 对话框动画 */
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-content-enter-active,
.dialog-content-leave-active {
  transition: all 0.3s ease;
}

.dialog-content-enter-from,
.dialog-content-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* 标签样式 */
.tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1;
  transition: all 0.2s ease;
}

.tag:hover {
  opacity: 0.8;
}

/* 加载动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading {
  animation: spin 1s linear infinite;
}
</style>
