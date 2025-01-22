<template>
  <div class="bg-white rounded-lg">
    <form @submit.prevent="handleSubmit" class="space-y-4 md:space-y-6">
      <!-- 标题 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">
          标题 <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.title"
          type="text"
          required
          placeholder="输入标题"
          class="w-full px-3 md:px-4 py-2.5 md:py-2 text-base md:text-sm rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          :class="{ 'border-red-500': errors.title }"
        />
        <p v-if="errors.title" class="mt-1.5 text-sm text-red-500">
          {{ errors.title }}
        </p>
      </div>

      <!-- 描述 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">
          描述 <span class="text-red-500">*</span>
        </label>
        <textarea
          v-model="form.description"
          required
          placeholder="输入描述"
          rows="3"
          class="w-full px-3 md:px-4 py-2.5 md:py-2 text-base md:text-sm rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          :class="{ 'border-red-500': errors.description }"
        ></textarea>
        <p v-if="errors.description" class="mt-1.5 text-sm text-red-500">
          {{ errors.description }}
        </p>
      </div>

      <!-- 提示词内容 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">
          提示词内容 <span class="text-red-500">*</span>
        </label>
        <textarea
          v-model="form.content"
          required
          placeholder="输入提示词内容"
          rows="6"
          class="w-full px-3 md:px-4 py-2.5 md:py-2 text-base md:text-sm rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
          :class="{ 'border-red-500': errors.content }"
        ></textarea>
        <p v-if="errors.content" class="mt-1.5 text-sm text-red-500">
          {{ errors.content }}
        </p>
      </div>

      <!-- 价格 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">
          价格(金币) <span class="text-red-500">*</span>
        </label>
        <div class="flex items-center gap-2">
          <input
            v-model.number="form.price"
            type="number"
            required
            min="1"
            class="w-28 md:w-32 px-3 md:px-4 py-2.5 md:py-2 text-base md:text-sm rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.price }"
          />
          <span class="text-gray-500">金币</span>
        </div>
        <p v-if="errors.price" class="mt-1.5 text-sm text-red-500">
          {{ errors.price }}
        </p>
      </div>

      <!-- 标签 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          标签
        </label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tag in availableTags"
            :key="tag.id"
            type="button"
            class="min-h-[40px] px-4 py-1.5 rounded-full text-base md:text-sm font-medium transition-colors"
            :class="
              form.tags.includes(tag.id)
                ? 'bg-blue-100 text-blue-700 border border-blue-200'
                : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
            "
            @click="toggleTag(tag.id)"
          >
            {{ tag.name }}
          </button>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex gap-3 pt-4 md:justify-end md:gap-4">
        <button
          type="button"
          class="flex-1 md:flex-none h-11 md:h-auto px-6 py-2.5 md:py-2 text-base md:text-sm rounded-lg border border-gray-300 hover:bg-gray-50"
          @click="$emit('cancel')"
        >
          取消
        </button>
        <button
          type="submit"
          class="flex-1 md:flex-none h-11 md:h-auto px-6 py-2.5 md:py-2 text-base md:text-sm rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="submitting"
        >
          {{ submitting ? "发布中..." : "发布" }}
        </button>
      </div>

      <!-- 平台规则说明 -->
      <div class="mt-6 p-4 bg-gray-50 rounded-lg text-base md:text-sm">
        <h3 class="text-lg font-medium text-gray-900 mb-2">发布规则</h3>
        <ul class="list-disc list-inside text-gray-600 space-y-1.5">
          <li>提示词内容必须原创，不得抄袭他人</li>
          <li>内容需要经过审核后才能上架</li>
          <li>
            价格范围: {{ marketSettings.min_price }} -
            {{ marketSettings.max_price }} 金币
          </li>
          <li>
            平台抽成比例:
            {{ (marketSettings.commission_rate * 100).toFixed(1) }}%
          </li>
        </ul>
      </div>
    </form>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";

// 定义组件的输入props
const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({}),
  },
  submitting: {
    type: Boolean,
    default: false,
  },
});

// 定义组件的输出事件
const emit = defineEmits(["submit", "cancel", "update:submitting"]);

// 表单数据
const form = reactive({
  title: "",
  description: "",
  content: "",
  price: 1,
  tags: [],
  ...props.initialData,
});

// 状态
const errors = reactive({});
const marketSettings = reactive({
  min_price: 1,
  max_price: 1000,
  commission_rate: 0.1,
  require_review: true,
});

// 可用标签列表
const availableTags = ref([]);

// 获取市场设置和标签列表
const initializeData = async () => {
  try {
    // 获取市场设置
    const settingsResponse = await request("/api/prompt-market/settings");
    Object.assign(marketSettings, settingsResponse);

    // 获取标签列表
    const tagsResponse = await request("/api/admin/tags");
    availableTags.value = tagsResponse;
  } catch (error) {
    ElMessage.error("初始化数据失败");
  }
};

// 切换标签选择
const toggleTag = (tagId) => {
  const index = form.tags.indexOf(tagId);
  if (index === -1) {
    form.tags.push(tagId);
  } else {
    form.tags.splice(index, 1);
  }
};

// 验证表单
const validateForm = () => {
  const newErrors = {};

  if (!form.title.trim()) {
    newErrors.title = "请输入标题";
  } else if (form.title.length > 100) {
    newErrors.title = "标题不能超过100个字符";
  }

  if (!form.description.trim()) {
    newErrors.description = "请输入描述";
  } else if (form.description.length > 500) {
    newErrors.description = "描述不能超过500个字符";
  }

  if (!form.content.trim()) {
    newErrors.content = "请输入提示词内容";
  } else if (form.content.length > 2000) {
    newErrors.content = "内容不能超过2000个字符";
  }

  if (
    !form.price ||
    form.price < marketSettings.min_price ||
    form.price > marketSettings.max_price
  ) {
    newErrors.price = `价格必须在 ${marketSettings.min_price} - ${marketSettings.max_price} 金币之间`;
  }

  Object.assign(errors, newErrors);
  return Object.keys(newErrors).length === 0;
};

// 处理表单提交
const handleSubmit = async () => {
  if (validateForm()) {
    emit("submit", {
      title: form.title,
      description: form.description,
      content: form.content,
      price: form.price,
      tags: form.tags,
    });
  }
};

// 生命周期钩子
onMounted(() => {
  initializeData();
});
</script>
<style scoped>
/* 移动端优化输入框 */
@media (max-width: 768px) {
  input[type="text"],
  input[type="number"],
  textarea {
    font-size: 16px; /* 防止iOS自动缩放 */
  }

  /* 增大点击区域 */
  label {
    padding: 4px 0;
  }

  /* 优化滚动条 */
  textarea {
    -webkit-overflow-scrolling: touch;
  }
}
</style>
