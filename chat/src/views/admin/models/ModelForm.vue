<template>
  <Transition name="fade">
    <div class="fixed inset-0 z-50">
      <!-- 背景遮罩 -->
      <div
        class="absolute inset-0 bg-gray-500/75 backdrop-blur-sm"
        @click="$emit('close')"
      />

      <!-- 弹窗主体 -->
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="relative w-full max-w-2xl bg-white shadow-xl rounded-xl">
          <!-- 弹窗头部 -->
          <div
            class="h-16 px-6 border-b border-gray-100/60 flex items-center justify-between"
          >
            <h3 class="text-xl font-semibold text-gray-800">
              {{ isEdit ? "编辑模型" : "添加模型" }}
            </h3>
            <button
              @click="$emit('close')"
              class="p-2 rounded-lg hover:bg-gray-100/80 transition-colors text-gray-500"
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

          <!-- 表单区域 -->
          <form
            @submit.prevent="handleSubmit"
            class="max-h-[calc(100vh-12rem)] overflow-y-auto"
          >
            <div class="px-6 py-6 space-y-6">
              <!-- 图片上传区域 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >模型图标</label
                >
                <div class="flex flex-col sm:flex-row sm:items-center gap-4">
                  <div
                    class="relative h-32 w-32 mx-auto sm:mx-0 rounded-xl overflow-hidden bg-gray-50 border border-gray-100/60"
                  >
                    <img
                      v-if="imagePreview"
                      :src="imagePreview"
                      class="h-full w-full object-cover"
                      alt="模型图标预览"
                    />
                    <div
                      v-else
                      class="h-full w-full flex items-center justify-center"
                    >
                      <svg
                        class="h-12 w-12 text-gray-300"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                    </div>
                  </div>

                  <div class="flex flex-col gap-2">
                    <input
                      type="file"
                      ref="fileInput"
                      @change="handleImageChange"
                      accept="image/*"
                      class="hidden"
                    />
                    <button
                      type="button"
                      @click="triggerFileInput"
                      class="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      {{ imagePreview ? "更改图片" : "上传图片" }}
                    </button>
                    <button
                      v-if="imagePreview"
                      type="button"
                      @click="removeImage"
                      class="px-4 py-2 border border-red-200 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-colors"
                    >
                      删除图片
                    </button>
                    <p class="text-xs text-gray-500">
                      支持 JPG、PNG 格式，建议尺寸 256x256 像素
                    </p>
                  </div>
                </div>
              </div>

              <!-- 基本信息输入区域 -->
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5"
                    >模型名称</label
                  >
                  <input
                    type="text"
                    v-model="formData.name"
                    required
                    class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1.5"
                    >所属公司</label
                  >
                  <input
                    type="text"
                    v-model="formData.company"
                    required
                    class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
                  />
                </div>
              </div>

              <!-- 标签区域 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >标签</label
                >
                <div class="space-y-3">
                  <div
                    class="min-h-[36px] p-2 border border-gray-200 rounded-lg bg-gray-50"
                  >
                    <div class="flex flex-wrap gap-2">
                      <div
                        v-for="(tag, index) in tags"
                        :key="index"
                        class="inline-flex items-center bg-blue-50 text-blue-600 px-2.5 py-1 rounded-lg text-sm"
                      >
                        {{ tag }}
                        <button
                          type="button"
                          @click="removeTag(index)"
                          class="ml-1.5 text-blue-400 hover:text-blue-600"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="flex gap-2">
                    <input
                      type="text"
                      v-model="newTag"
                      @keydown.enter.prevent="addTag"
                      placeholder="输入标签后按回车添加"
                      class="flex-1 rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
                    />
                    <button
                      type="button"
                      @click="addTag"
                      class="px-4 py-2.5 bg-blue-50 text-blue-600 rounded-lg text-sm hover:bg-blue-100 transition-colors"
                    >
                      添加
                    </button>
                  </div>
                </div>
              </div>

              <!-- 描述输入框 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5"
                  >描述</label
                >
                <textarea
                  v-model="formData.description"
                  rows="3"
                  required
                  class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
                ></textarea>
              </div>

              <!-- 分组选择 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5"
                  >分组</label
                >
                <select
                  v-model="formData.group"
                  required
                  class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
                >
                  <option value="free">免费</option>
                  <option value="vip">VIP</option>
                  <option value="coin">金币</option>
                </select>
              </div>
              <p class="mt-1.5 text-xs text-gray-500">
                如果有与该模型同名的其他分组的模型,则可能会受到影响,可以通过修改映射解决
              </p>
              <!-- 渠道选择 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5"
                  >绑定渠道</label
                >
                <div class="relative">
                  <Listbox v-model="selectedChannels" multiple>
                    <div class="relative">
                      <ListboxButton
                        class="w-full cursor-pointer rounded-lg bg-white py-2.5 px-4 text-left border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
                      >
                        <span class="block truncate text-sm">
                          {{
                            selectedChannels.length
                              ? `已选择 ${selectedChannels.length} 个渠道`
                              : "请选择渠道"
                          }}
                        </span>
                      </ListboxButton>
                      <ListboxOptions
                        class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-lg bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                      >
                        <ListboxOption
                          v-for="channel in channels"
                          :key="channel.id"
                          :value="channel.id"
                          v-slot="{ active, selected }"
                        >
                          <div
                            :class="[
                              'flex items-center px-4 py-2 cursor-pointer text-sm',
                              active ? 'bg-blue-50' : '',
                            ]"
                          >
                            <input
                              type="checkbox"
                              :checked="selected"
                              class="mr-3"
                            />
                            <span>{{ channel.channel_name }}</span>
                          </div>
                        </ListboxOption>
                      </ListboxOptions>
                    </div>
                  </Listbox>
                </div>
                <p class="mt-1.5 text-xs text-gray-500">
                  绑定后模型将只使用选中的渠道,不选择则随机使用所有支持该模型的渠道
                </p>
              </div>

              <!-- 金币价格设置 -->
              <div v-if="formData.group === 'coin'" class="space-y-2">
                <label class="block text-sm font-medium text-gray-700"
                  >金币价格设置</label
                >
                <div class="flex items-center gap-2">
                  <input
                    type="number"
                    v-model="formData.coinPrice"
                    min="0"
                    required
                    placeholder="输入金币数"
                    class="w-32 rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
                  />
                  <span class="text-sm text-gray-500">金币</span>
                </div>
              </div>

              <!-- 排序序号设置 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5"
                  >排序序号</label
                >
                <input
                  type="number"
                  v-model="formData.sort_order"
                  min="0"
                  placeholder="数字越小排序越靠前，默认为0"
                  class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
                />
                <p class="mt-1.5 text-xs text-gray-500">
                  数字越小排在越前面，相同数字按名称排序
                </p>
              </div>

              <!-- 错误提示 -->
              <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
            </div>

            <!-- 底部按钮栏 -->
            <div
              class="h-16 px-6 border-t border-gray-100/60 flex items-center justify-end gap-3"
            >
              <button
                type="button"
                @click="$emit('close')"
                class="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {{ isSubmitting ? "提交中..." : isEdit ? "保存" : "创建" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import {
  Listbox,
  ListboxButton,
  ListboxOptions,
  ListboxOption,
} from "@headlessui/vue";
import { request } from "@/utils/request";

const props = defineProps({
  model: { type: Object, default: null },
  isEdit: { type: Boolean, default: false },
});

// 添加必要的样式定义
const style = `
<style>
/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 自定义滚动条样式 */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #E5E7EB transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #E5E7EB;
  border-radius: 3px;
}

/* 确保模态框内容区域可以正确滚动 */
@media (max-height: 800px) {
  .dialog-content {
    max-height: calc(100vh - 12rem);
    overflow-y: auto;
  }
}
</style>
`;

const emit = defineEmits(["close", "submit"]);

// 表单数据
const formData = ref({
  name: "",
  company: "",
  description: "",
  group: "free",
  is_active: true,
  coinPrice: 0,
  sort_order: 0,
});

// 状态变量
const error = ref("");
const isSubmitting = ref(false);
const tags = ref([]);
const newTag = ref("");
const fileInput = ref(null);
const imagePreview = ref("");
const imageFile = ref(null);
const channels = ref([]);
const selectedChannels = ref([]);

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click();
};

// 处理图片上传
const handleImageChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    // 验证文件类型
    if (!file.type.startsWith("image/")) {
      error.value = "请上传图片文件";
      return;
    }

    // 验证文件大小（2MB）
    if (file.size > 2 * 1024 * 1024) {
      error.value = "图片大小不能超过 2MB";
      return;
    }

    imageFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target.result;
    };
    reader.onerror = () => {
      error.value = "图片读取失败";
    };
    reader.readAsDataURL(file);
  }
};

// 移除图片
const removeImage = () => {
  imageFile.value = null;
  imagePreview.value = "";
  if (fileInput.value) {
    fileInput.value.value = "";
  }
  formData.value.icon = null;
};

// 标签操作
const addTag = () => {
  const tag = newTag.value.trim();
  if (tag && !tags.value.includes(tag)) {
    tags.value.push(tag);
    newTag.value = "";
  }
};

const removeTag = (index) => {
  tags.value.splice(index, 1);
};

// 监听分组变化
watch(
  () => formData.value.group,
  (newGroup) => {
    if (newGroup !== "coin") {
      formData.value.coinPrice = 0;
    }
  }
);

// 表单提交处理
const handleSubmit = async () => {
  try {
    isSubmitting.value = true;
    error.value = "";

    // 构建表单数据
    const form = new FormData();
    form.append("name", formData.value.name);
    form.append("company", formData.value.company);
    form.append("tags", tags.value.join(","));
    form.append("description", formData.value.description);
    form.append("group", formData.value.group);
    form.append("sort_order", formData.value.sort_order);
    form.append("is_active", formData.value.is_active);

    // 添加选中的渠道
    if (selectedChannels.value.length > 0) {
      form.append("channel_ids", JSON.stringify(selectedChannels.value));
    }

    // 添加金币价格
    if (formData.value.group === "coin") {
      form.append("coinPrice", formData.value.coinPrice);
    }

    // 添加图片
    if (imageFile.value) {
      form.append("icon", imageFile.value);
    }

    // 发送请求
    const url = props.isEdit
      ? `/api/admin/models/${props.model.id}`
      : "/api/admin/models";

    const response = await request(url, {
      method: props.isEdit ? "PUT" : "POST",
      body: form,
    });

    emit("submit", response);
    emit("close");
  } catch (err) {
    error.value = err.message || "提交失败";
  } finally {
    isSubmitting.value = false;
  }
};

// 组件挂载时获取数据
onMounted(async () => {
  try {
    // 获取渠道列表
    const channelsResponse = await request("/api/admin/channels");
    channels.value = channelsResponse;

    // 如果是编辑模式，获取该模型已绑定的渠道
    if (props.isEdit && props.model) {
      const bindingsResponse = await request(
        `/api/admin/models/${props.model.id}/channels`
      );
      selectedChannels.value = bindingsResponse.map(
        (binding) => binding.channel_id
      );
    }

    // 填充表单数据
    if (props.model) {
      formData.value = {
        name: props.model.name,
        company: props.model.company,
        description: props.model.description || "",
        group: props.model.group,
        is_active: props.model.is_active,
        coinPrice: props.model.price?.price || 0,
        sort_order: props.model.sort_order || 0,
      };
      // 设置标签
      tags.value = props.model.tags
        ? props.model.tags.split(",").filter(Boolean)
        : [];
      // 设置图片预览
      if (props.model.icon) {
        imagePreview.value = props.model.icon;
      }
    }
  } catch (err) {
    console.error("获取数据失败:", err);
    error.value = "获取数据失败";
  }
});
</script>
