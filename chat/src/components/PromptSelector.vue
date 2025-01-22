<template>
  <div class="prompt-selector">
    <!-- 标签切换和搜索区域 -->
    <div class="p-3 border-y">
      <!-- 标签页切换按钮 -->
      <div class="flex mb-3">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="currentTab = tab.value"
          class="flex-1 px-4 py-2 border"
          :class="[
            currentTab === tab.value
              ? 'text-blue-600 bg-blue-50 border-blue-500'
              : 'text-gray-600 hover:text-gray-800 border-gray-200',
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 搜索栏 -->
      <div class="relative">
        <Search
          class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
        />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索提示词..."
          class="w-full pl-9 pr-4 py-2 border rounded focus:outline-none focus:border-blue-500"
        />
      </div>
    </div>

    <!-- 市场提示词面板 -->
    <div v-show="currentTab === 'product'" class="p-3 relative">
      <div
        class="flex gap-2 overflow-x-auto pb-2 hide-scrollbar"
        ref="marketScroll"
      >
        <div
          v-for="prompt in filteredMarketPrompts"
          :key="prompt.id"
          class="flex-shrink-0 w-40 p-3 border rounded cursor-pointer transition-colors"
          :class="
            selectedPrompt?.id === prompt.id &&
            selectedPrompt?.type === 'product'
              ? 'border-blue-500'
              : 'hover:border-gray-400'
          "
          @click="selectPrompt(prompt, 'product')"
        >
          <div class="text-sm font-medium truncate">{{ prompt.title }}</div>
          <div class="text-xs text-gray-500 mt-1 truncate">
            {{ prompt.description }}
          </div>
          <div v-if="prompt.tags?.length" class="flex flex-wrap gap-1 mt-2">
            <span
              v-for="(tag, index) in prompt.tags.slice(0, 3)"
              :key="tag.id"
              class="text-xs px-2 py-0.5 rounded"
              :style="{ backgroundColor: tag.color + '20', color: tag.color }"
            >
              {{ tag.name }}
            </span>
            <span v-if="prompt.tags.length > 3" class="text-xs text-gray-500">
              +{{ prompt.tags.length - 3 }}
            </span>
          </div>
        </div>

        <!-- 无搜索结果提示 -->
        <div
          v-if="filteredMarketPrompts.length === 0"
          class="w-full text-center py-8 text-gray-500"
        >
          未找到匹配的市场提示词
        </div>
      </div>
      <!-- 滚动按钮 -->
      <button
        v-if="showMarketLeftScroll"
        @click="scroll('market', -200)"
        class="absolute left-0 top-1/2 -translate-y-1/2 bg-white shadow rounded-full p-1 hover:bg-gray-50"
      >
        <ChevronLeft class="w-4 h-4" />
      </button>
      <button
        v-if="showMarketRightScroll"
        @click="scroll('market', 200)"
        class="absolute right-0 top-1/2 -translate-y-1/2 bg-white shadow rounded-full p-1 hover:bg-gray-50"
      >
        <ChevronRight class="w-4 h-4" />
      </button>
    </div>

    <!-- 私人提示词面板 -->
    <div v-show="currentTab === 'private'" class="p-3 relative">
      <div
        class="flex gap-2 overflow-x-auto pb-2 hide-scrollbar"
        ref="privateScroll"
      >
        <div
          v-for="prompt in filteredPrivatePrompts"
          :key="prompt.id"
          class="flex-shrink-0 w-40 p-3 border rounded cursor-pointer transition-colors"
          :class="
            selectedPrompt?.id === prompt.id &&
            selectedPrompt?.type === 'private'
              ? 'border-blue-500'
              : 'hover:border-gray-400'
          "
          @click="selectPrompt(prompt, 'private')"
        >
          <div class="text-sm font-medium truncate">{{ prompt.title }}</div>
          <div class="text-xs text-gray-500 mt-1 truncate">
            {{ prompt.description }}
          </div>
          <div v-if="prompt.tags?.length" class="flex flex-wrap gap-1 mt-2">
            <span
              v-for="(tag, index) in prompt.tags.slice(0, 3)"
              :key="tag.id"
              class="text-xs px-2 py-0.5 rounded"
              :style="{ backgroundColor: tag.color + '20', color: tag.color }"
            >
              {{ tag.name }}
            </span>
            <span v-if="prompt.tags.length > 3" class="text-xs text-gray-500">
              +{{ prompt.tags.length - 3 }}
            </span>
          </div>
        </div>

        <!-- 无搜索结果提示 -->
        <div
          v-if="filteredPrivatePrompts.length === 0"
          class="w-full text-center py-8 text-gray-500"
        >
          未找到匹配的私人提示词
        </div>
      </div>
      <!-- 滚动按钮 -->
      <button
        v-if="showPrivateLeftScroll"
        @click="scroll('private', -200)"
        class="absolute left-0 top-1/2 -translate-y-1/2 bg-white shadow rounded-full p-1 hover:bg-gray-50"
      >
        <ChevronLeft class="w-4 h-4" />
      </button>
      <button
        v-if="showPrivateRightScroll"
        @click="scroll('private', 200)"
        class="absolute right-0 top-1/2 -translate-y-1/2 bg-white shadow rounded-full p-1 hover:bg-gray-50"
      >
        <ChevronRight class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue";
import { request } from "@/utils/request";
import { ChevronLeft, ChevronRight, Search } from "lucide-vue-next";

const props = defineProps({
  modelValue: Object,
});

const emit = defineEmits(["update:modelValue"]);

// 标签页配置
const tabs = [
  { label: "市场提示词", value: "product" }, // 修改为 product
  { label: "私人提示词", value: "private" },
];

const currentTab = ref("product"); // 修改为 product
const searchQuery = ref("");
const marketPrompts = ref([]);
const privatePrompts = ref([]);
const marketScroll = ref(null);
const privateScroll = ref(null);

const showMarketLeftScroll = ref(false);
const showMarketRightScroll = ref(false);
const showPrivateLeftScroll = ref(false);
const showPrivateRightScroll = ref(false);

const selectedPrompt = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

// 过滤市场提示词
const filteredMarketPrompts = computed(() => {
  if (!searchQuery.value) return marketPrompts.value;

  const query = searchQuery.value.toLowerCase();
  return marketPrompts.value.filter(
    (prompt) =>
      prompt.title.toLowerCase().includes(query) ||
      prompt.description.toLowerCase().includes(query) ||
      prompt.tags?.some((tag) => tag.name.toLowerCase().includes(query))
  );
});

// 过滤私人提示词
const filteredPrivatePrompts = computed(() => {
  if (!searchQuery.value) return privatePrompts.value;

  const query = searchQuery.value.toLowerCase();
  return privatePrompts.value.filter(
    (prompt) =>
      prompt.title.toLowerCase().includes(query) ||
      prompt.description.toLowerCase().includes(query)
  );
});

// 加载提示词数据
const loadPrompts = async () => {
  try {
    // 加载市场提示词
    const marketResponse = await request("/api/prompts?limit=20");
    marketPrompts.value = marketResponse.data.map((prompt) => ({
      ...prompt,
      tags: prompt.tags || [],
    }));

    // 加载私人提示词
    const privateResponse = await request("/api/private-prompts");
    privatePrompts.value = privateResponse.map((prompt) => ({
      ...prompt,
      tags: prompt.tags || [],
    }));

    // 检查滚动状态
    await nextTick();
    checkScroll("market");
    checkScroll("private");
  } catch (error) {
    console.error("加载提示词失败:", error);
    marketPrompts.value = [];
    privatePrompts.value = [];
  }
};

onMounted(loadPrompts);

const checkScroll = (type) => {
  const el = type === "market" ? marketScroll.value : privateScroll.value;
  if (!el) return;

  if (type === "market") {
    showMarketLeftScroll.value = el.scrollLeft > 0;
    showMarketRightScroll.value =
      el.scrollWidth > el.clientWidth &&
      el.scrollLeft < el.scrollWidth - el.clientWidth;
  } else {
    showPrivateLeftScroll.value = el.scrollLeft > 0;
    showPrivateRightScroll.value =
      el.scrollWidth > el.clientWidth &&
      el.scrollLeft < el.scrollWidth - el.clientWidth;
  }
};

const scroll = (type, amount) => {
  const el = type === "market" ? marketScroll.value : privateScroll.value;
  if (!el) return;

  el.scrollBy({
    left: amount,
    behavior: "smooth",
  });

  setTimeout(() => checkScroll(type), 300);
};

const selectPrompt = (prompt, type) => {
  selectedPrompt.value = {
    ...prompt,
    type, // 这里传入的 type 已经是 'product' 或 'private'
  };
};

watch(searchQuery, () => {
  nextTick(() => {
    checkScroll("market");
    checkScroll("private");
  });
});

// 监听滚动
watch(marketScroll, (el) => {
  if (el) {
    el.addEventListener("scroll", () => checkScroll("market"));
  }
});

watch(privateScroll, (el) => {
  if (el) {
    el.addEventListener("scroll", () => checkScroll("private"));
  }
});
</script>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
