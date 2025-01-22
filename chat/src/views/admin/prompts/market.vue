<!-- src/views/PromptMarket.vue -->
<template>
  <div
    class="space-y-4 md:space-y-6 max-w-7xl mx-auto px-4 md:px-6 py-4 md:py-6"
  >
    <h1 class="text-xl md:text-2xl font-bold">提示词市场</h1>

    <!-- 统计信息卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
      <el-card shadow="hover" class="stats-card !border-0">
        <div class="flex justify-between items-center">
          <div>
            <div class="text-xs md:text-sm font-medium text-gray-500">
              总提示词数
            </div>
            <div
              class="mt-1.5 md:mt-2 text-xl md:text-3xl font-bold text-gray-900"
            >
              {{ stats.totalPrompts }}
            </div>
          </div>
          <Store class="h-6 w-6 md:h-8 md:w-8 text-purple-500" />
        </div>
      </el-card>

      <el-card shadow="hover" class="stats-card !border-0">
        <div class="flex justify-between items-center">
          <div>
            <div class="text-xs md:text-sm font-medium text-gray-500">
              待审核数
            </div>
            <div
              class="mt-1.5 md:mt-2 text-xl md:text-3xl font-bold text-orange-600"
            >
              {{ stats.pendingReviews }}
            </div>
          </div>
          <Clock class="h-6 w-6 md:h-8 md:w-8 text-orange-500" />
        </div>
      </el-card>

      <el-card shadow="hover" class="stats-card !border-0">
        <div class="flex justify-between items-center">
          <div>
            <div class="text-xs md:text-sm font-medium text-gray-500">
              今日购买
            </div>
            <div
              class="mt-1.5 md:mt-2 text-xl md:text-3xl font-bold text-green-600"
            >
              {{ stats.todayPurchases }}
            </div>
          </div>
          <div class="h-6 w-6 md:h-8 md:w-8 rounded-full bg-green-100"></div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stats-card !border-0">
        <div class="flex justify-between items-center">
          <div>
            <div class="text-xs md:text-sm font-medium text-gray-500">
              平均满意度
            </div>
            <div
              class="mt-1.5 md:mt-2 text-xl md:text-3xl font-bold text-blue-600"
            >
              99999%
            </div>
          </div>
          <ThumbsUp class="h-6 w-6 md:h-8 md:w-8 text-blue-500" />
        </div>
      </el-card>
    </div>

    <!-- 操作栏 -->
    <div class="bg-white rounded-lg shadow p-3 md:p-4 space-y-3">
      <div class="filter-container">
        <!-- 状态筛选 -->
        <el-select v-model="filters.status" placeholder="全部状态">
          <el-option
            v-for="status in statusOptions"
            :key="status.value"
            :label="status.label"
            :value="status.value"
          />
        </el-select>

        <!-- 标签筛选器 -->
        <el-select
          v-model="filters.tags"
          multiple
          filterable
          clearable
          collapse-tags
          placeholder="选择标签"
          @change="handleTagSelect"
          class="!w-full md:!w-auto"
        >
          <el-option-group
            v-for="group in tagGroups"
            :key="group.type"
            :label="group.label"
          >
            <el-option
              v-for="tag in group.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            >
              <span class="flex items-center">
                <span
                  class="w-3 h-3 rounded-full mr-2"
                  :style="{ backgroundColor: tag.color }"
                ></span>
                {{ tag.name }}
              </span>
            </el-option>
          </el-option-group>
        </el-select>
      </div>

      <div class="flex flex-wrap gap-2">
        <el-button @click="refreshData" class="!flex-1 md:!flex-none">
          <RefreshCw class="w-4 h-4 mr-2" />
          刷新
        </el-button>

        <el-button @click="openSettings" class="!flex-1 md:!flex-none">
          <Settings class="w-4 h-4 mr-2" />
          设置
        </el-button>

        <el-button @click="openTagsManager" class="!flex-1 md:!flex-none">
          <Tags class="w-4 h-4 mr-2" />
          标签
        </el-button>
      </div>

      <el-button
        type="primary"
        @click="openCreatePrompt"
        class="!w-full md:!w-auto"
      >
        <PlusCircle class="w-4 h-4 mr-2" />
        新建提示词
      </el-button>
    </div>

    <!-- 提示词卡片网格 -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-6">
      <PromptCard
        v-for="prompt in prompts"
        :key="prompt.id"
        :prompt="prompt"
        :isAdmin="true"
        :currentUserId="userId"
        @view="viewPrompt"
        @review="reviewPrompt"
        @delist="delistPrompt"
        @list="listPrompt"
        @manageTags="openTagManager"
        @delete="deletePrompt"
        @vote="handleVote"
        @purchase="handlePurchase"
        @use="handleUsePrompt"
      />
    </div>

    <!-- 分页 -->
    <div class="mt-4">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[9, 18, 36]"
        :total="total"
        :pager-count="isMobile ? 3 : 7"
        layout="total, sizes, prev, pager, next"
        class="flex justify-center"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="dialogVisible.detail"
      title="提示词详情"
      :width="isMobile ? '95%' : '800px'"
      :center="true"
      :append-to-body="true"
      class="detail-dialog"
    >
      <el-descriptions
        :column="1"
        border
        class="descriptions-mobile md:descriptions-desktop"
      >
        <el-descriptions-item label="标题">
          {{ selectedPrompt?.title }}
        </el-descriptions-item>
        <el-descriptions-item label="描述">
          {{ selectedPrompt?.description }}
        </el-descriptions-item>
        <el-descriptions-item label="标签">
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tag in selectedPrompt?.tags"
              :key="tag.id"
              class="px-2 py-0.5 rounded-full text-xs font-medium"
              :style="{
                backgroundColor: tag.color + '20',
                color: tag.color,
                border: `1px solid ${tag.color}`,
              }"
            >
              {{ tag.name }}
            </span>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="内容">
          <div class="bg-gray-50 p-4 rounded whitespace-pre-wrap">
            {{ selectedPrompt?.content }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="创建者">
          {{ selectedPrompt?.creator_username }}
        </el-descriptions-item>
        <el-descriptions-item label="价格">
          {{ selectedPrompt?.price }} 金币
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 设置弹窗 -->
    <el-dialog
      v-model="dialogVisible.settings"
      title="市场设置"
      :width="isMobile ? '95%' : '500px'"
      :top="isMobile ? '20px' : '15vh'"
    >
      <el-form :model="settings" label-width="100px">
        <el-form-item label="抽成比例">
          <el-input-number
            v-model="settings.commission_rate"
            :min="0"
            :max="1"
            :step="0.01"
            :precision="2"
            class="!w-full"
          />
        </el-form-item>
        <el-form-item label="需要审核">
          <el-switch v-model="settings.require_review" />
        </el-form-item>
        <el-form-item label="价格限制">
          <el-row :gutter="12">
            <el-col :span="12">
              <el-input-number
                v-model="settings.min_price"
                :min="0"
                placeholder="最低价格"
                class="!w-full"
              />
            </el-col>
            <el-col :span="12">
              <el-input-number
                v-model="settings.max_price"
                :min="0"
                placeholder="最高价格"
                class="!w-full"
              />
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="dialogVisible.settings = false">取消</el-button>
          <el-button type="primary" @click="saveSettings">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 创建提示词弹窗 -->
    <el-dialog
      v-model="dialogVisible.createPrompt"
      title="新建提示词"
      :width="isMobile ? '95%' : '800px'"
      :top="isMobile ? '20px' : '15vh'"
    >
      <el-form :model="promptForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="promptForm.title" placeholder="输入提示词标题" />
        </el-form-item>

        <el-form-item label="描述" required>
          <el-input
            v-model="promptForm.description"
            type="textarea"
            :rows="3"
            placeholder="输入提示词描述"
          />
        </el-form-item>

        <el-form-item label="内容" required>
          <el-input
            v-model="promptForm.content"
            type="textarea"
            :rows="6"
            placeholder="输入提示词内容"
          />
        </el-form-item>

        <el-form-item label="价格" required>
          <el-input-number
            v-model="promptForm.price"
            :min="settings.min_price"
            :max="settings.max_price"
            class="!w-full"
          />
        </el-form-item>

        <el-form-item label="标签">
          <el-select
            v-model="promptForm.tags"
            multiple
            filterable
            placeholder="选择标签"
            class="!w-full"
          >
            <el-option-group
              v-for="group in tagGroups"
              :key="group.type"
              :label="group.label"
            >
              <el-option
                v-for="tag in group.tags"
                :key="tag.id"
                :label="tag.name"
                :value="tag.id"
              >
                <span class="flex items-center">
                  <span
                    class="w-3 h-3 rounded-full mr-2"
                    :style="{ backgroundColor: tag.color }"
                  ></span>
                  {{ tag.name }}
                </span>
              </el-option>
            </el-option-group>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="dialogVisible.createPrompt = false"
            >取消</el-button
          >
          <el-button type="primary" @click="createPrompt">创建</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 标签管理弹窗 -->
    <el-dialog
      v-model="dialogVisible.tags"
      :title="
        selectedPrompt ? '管理标签 - ' + selectedPrompt.title : '标签管理'
      "
      :width="isMobile ? '95%' : '500px'"
      :top="isMobile ? '20px' : '15vh'"
    >
      <div v-if="selectedPrompt" class="space-y-4">
        <div class="flex flex-wrap gap-2">
          <span
            v-for="tag in selectedPrompt.tags"
            :key="tag.id"
            class="px-2 py-1 rounded-full text-sm font-medium flex items-center gap-2"
            :style="{
              backgroundColor: tag.color + '20',
              color: tag.color,
              border: `1px solid ${tag.color}`,
            }"
          >
            {{ tag.name }}
            <XCircle
              class="w-4 h-4 cursor-pointer hover:text-red-500"
              @click="removeTag(selectedPrompt, tag)"
            />
          </span>
        </div>

        <el-select
          v-model="selectedTags"
          multiple
          filterable
          placeholder="选择标签"
          class="!w-full"
        >
          <el-option-group
            v-for="group in availableTagGroups"
            :key="group.type"
            :label="group.label"
          >
            <el-option
              v-for="tag in group.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            >
              <span class="flex items-center">
                <span
                  class="w-3 h-3 rounded-full mr-2"
                  :style="{ backgroundColor: tag.color }"
                ></span>
                {{ tag.name }}
              </span>
            </el-option>
          </el-option-group>
        </el-select>
        <div class="flex justify-end mt-4">
          <el-button type="primary" @click="addTags">添加标签</el-button>
        </div>
      </div>

      <div v-else class="space-y-4">
        <!-- 标签列表 -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base md:text-lg font-medium">标签列表</h3>
          <el-button type="primary" size="small" @click="openCreateTag">
            新建标签
          </el-button>
        </div>

        <el-table :data="allTags" stripe>
          <el-table-column prop="name" label="名称" min-width="120">
            <template #default="{ row }">
              <span class="flex items-center">
                <span
                  class="w-3 h-3 rounded-full mr-2"
                  :style="{ backgroundColor: row.color }"
                ></span>
                {{ row.name }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" min-width="100">
            <template #default="{ row }">
              {{ getTagTypeText(row.type) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="description"
            label="描述"
            min-width="150"
            show-overflow-tooltip
          />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="editTag(row)">
                编辑
              </el-button>
              <el-button link type="danger" @click="deleteTag(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 创建/编辑标签弹窗 -->
    <el-dialog
      v-model="dialogVisible.tagForm"
      :title="tagForm.id ? '编辑标签' : '新建标签'"
      :width="isMobile ? '95%' : '500px'"
      :top="isMobile ? '20px' : '15vh'"
    >
      <el-form :model="tagForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="tagForm.name" placeholder="输入标签名称" />
        </el-form-item>

        <el-form-item label="颜色" required>
          <el-color-picker v-model="tagForm.color" class="!w-full" />
        </el-form-item>

        <el-form-item label="类型" required>
          <el-select
            v-model="tagForm.type"
            placeholder="选择标签类型"
            class="!w-full"
          >
            <el-option
              v-for="type in tagTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="tagForm.description"
            type="textarea"
            placeholder="输入标签描述"
          />
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number
            v-model="tagForm.sort_order"
            :min="0"
            class="!w-full"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="dialogVisible.tagForm = false">取消</el-button>
          <el-button type="primary" @click="saveTag">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Store,
  Clock,
  Settings,
  RefreshCw,
  PlusCircle,
  ThumbsUp,
  XCircle,
  Tags,
} from "lucide-vue-next";
import { request } from "@/utils/request";
import PromptCard from "@/components/PromptCard.vue";

// 状态
const loading = ref(false);
const page = ref(1);
const pageSize = ref(9);
const total = ref(0);
const prompts = ref([]);
const selectedPrompt = ref(null);
const selectedTags = ref([]);
const isMobile = ref(false);
// 标签相关
const allTags = ref([]);
const tagForm = ref({
  name: "",
  color: "#1677FF",
  type: "category",
  description: "",
  sort_order: 0,
});

// 标签类型选项
const tagTypes = [
  { label: "分类标签", value: "category" },
  { label: "等级标签", value: "level" },
  { label: "特性标签", value: "feature" },
];

// 统计数据
const stats = ref({
  totalPrompts: 0,
  pendingReviews: 0,
  todayPurchases: 0,
});

// 筛选条件
const filters = ref({
  status: "",
  tags: [],
});

const handleTagSelect = (value) => {
  filters.value.tags = value;
  loadData();
};
// 弹窗控制
const dialogVisible = ref({
  detail: false,
  settings: false,
  tags: false,
  tagForm: false,
  createPrompt: false,
});

// 市场设置
const settings = ref({
  commission_rate: 0.1,
  require_review: true,
  min_price: 1,
  max_price: 1000,
});

// 打开创建提示词弹窗
const openCreatePrompt = () => {
  dialogVisible.value.createPrompt = true;
};

// 状态选项
const statusOptions = [
  { label: "全部", value: "" }, // 添加全部选项
  { label: "待审核", value: "pending" },
  { label: "已通过", value: "approved" },
  { label: "已拒绝", value: "rejected" },
  { label: "已下架", value: "delisted" },
];

// 计算属性：标签分组
const tagGroups = computed(() => {
  const groups = {};
  allTags.value.forEach((tag) => {
    if (!groups[tag.type]) {
      groups[tag.type] = {
        type: tag.type,
        label: getTagTypeText(tag.type),
        tags: [],
      };
    }
    groups[tag.type].tags.push(tag);
  });
  return Object.values(groups);
});

// 计算属性：可用的标签分组(排除已选择的)
const availableTagGroups = computed(() => {
  if (!selectedPrompt.value) return [];

  const selectedTagIds = new Set(selectedPrompt.value.tags.map((t) => t.id));
  const groups = {};

  allTags.value
    .filter((tag) => !selectedTagIds.has(tag.id))
    .forEach((tag) => {
      if (!groups[tag.type]) {
        groups[tag.type] = {
          type: tag.type,
          label: getTagTypeText(tag.type),
          tags: [],
        };
      }
      groups[tag.type].tags.push(tag);
    });

  return Object.values(groups);
});

// 获取标签类型文本
const getTagTypeText = (type) => {
  const typeMap = {
    category: "分类标签",
    level: "等级标签",
    feature: "特性标签",
  };
  return typeMap[type] || type;
};

//  loadData 函数
const loadData = async () => {
  loading.value = true;
  try {
    // 构建查询参数
    const params = new URLSearchParams({
      page: page.value,
      size: pageSize.value,
    });

    // 添加标签过滤
    if (filters.value.tags && filters.value.tags.length > 0) {
      filters.value.tags.forEach((tagId) => {
        params.append("tags[]", tagId);
      });
    }

    // 添加状态过滤
    if (filters.value.status) {
      params.append("status", filters.value.status);
    }

    const data = await request(`/api/admin/prompt-market/products?${params}`);
    prompts.value = data.items;
    total.value = data.total;
  } catch (error) {
    ElMessage.error({
      message: "加载数据失败",
      plain: true,
    });
  } finally {
    loading.value = false;
  }
};

// 添加筛选条件变化的监听
watch(
  () => ({
    status: filters.value.status,
    tags: [...filters.value.tags],
  }),
  () => {
    page.value = 1; // 重置到第一页
    loadData();
  },
  { deep: true }
);
// 加载标签
const loadTags = async () => {
  try {
    const data = await request("/api/admin/tags");
    allTags.value = data;
  } catch (error) {
    ElMessage.error({
      message: "加载标签失败",
      plain: true,
    });
  }
};

// 加载统计
const loadStats = async () => {
  try {
    const data = await request("/api/admin/prompt-market/stats");
    stats.value = data;
  } catch (error) {
    ElMessage.error({
      message: "加载统计数据失败",
      plain: true,
    });
  }
};

// 刷新数据
const refreshData = () => {
  loadData();
  loadStats();
};

// 查看详情
const viewPrompt = (prompt) => {
  selectedPrompt.value = prompt;
  dialogVisible.value.detail = true;
};

// 审核提示词
const reviewPrompt = async (prompt, action) => {
  try {
    await request(
      `/api/admin/prompt-market/products/${prompt.id}/review?action=${action}`,
      { method: "POST" }
    );
    ElMessage.success({
      message: "审核完成",
      plain: true,
    });
    refreshData();
  } catch (error) {
    ElMessage.error({
      message: "审核失败",
      plain: true,
    });
  }
};

// 下架提示词
const delistPrompt = async (prompt) => {
  try {
    await request(`/api/admin/prompt-market/products/${prompt.id}/delist`, {
      method: "POST",
    });
    ElMessage.success({
      message: "已下架",
      plain: true,
    });
    refreshData();
  } catch (error) {
    ElMessage.error({
      message: "下架失败",
      plain: true,
    });
  }
};

// 上架提示词
const listPrompt = async (prompt) => {
  try {
    await request(`/api/admin/prompt-market/products/${prompt.id}/list`, {
      method: "POST",
    });
    ElMessage.success({
      message: "上架成功",
      plain: true,
    });
    refreshData();
  } catch (error) {
    ElMessage.error({
      message: "上架失败",
      plain: true,
    });
  }
};

// 删除提示词
const deletePrompt = async (prompt) => {
  try {
    await ElMessageBox.confirm(
      "确定要删除这个提示词吗？此操作不可恢复。",
      "警告",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await request(`/api/admin/prompt-market/products/${prompt.id}`, {
      method: "DELETE",
    });
    ElMessage.success({
      message: "删除成功",
      plain: true,
    });
    refreshData();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error({
        message: "删除失败",
        plain: true,
      });
    }
  }
};

const promptForm = ref({
  title: "",
  description: "",
  content: "",
  price: settings.value.min_price,
  tags: [],
});

// 创建提示词方法
// 添加创建提示词的方法
const createPrompt = async () => {
  try {
    await request("/api/prompt-market/products", {
      // 修改这里的 URL
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(promptForm.value),
    });

    ElMessage.success({
      message: "创建成功",
      plain: true,
    });
    dialogVisible.value.createPrompt = false;

    // 重置表单
    promptForm.value = {
      title: "",
      description: "",
      content: "",
      price: 1,
    };

    // 刷新列表
    refreshData();
  } catch (error) {
    ElMessage.error({
      message: "创建失败",
      plain: true,
    });
  }
};
// 打开标签管理
const openTagsManager = () => {
  selectedPrompt.value = null;
  dialogVisible.value.tags = true;
};

// 打开提示词标签管理
const openTagManager = (prompt) => {
  selectedPrompt.value = prompt;
  selectedTags.value = [];
  dialogVisible.value.tags = true;
};

// 打开创建标签
const openCreateTag = () => {
  tagForm.value = {
    name: "",
    color: "#1677FF",
    type: "category",
    description: "",
    sort_order: 0,
  };
  dialogVisible.value.tagForm = true;
};

// 编辑标签
const editTag = (tag) => {
  tagForm.value = { ...tag };
  dialogVisible.value.tagForm = true;
};

// 保存标签
const saveTag = async () => {
  try {
    const method = tagForm.value.id ? "PUT" : "POST";
    const url = tagForm.value.id
      ? `/api/admin/tags/${tagForm.value.id}`
      : "/api/admin/tags";

    await request(url, {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(tagForm.value),
    });

    ElMessage.success({
      message: "保存成功",
      plain: true,
    });
    dialogVisible.value.tagForm = false;
    loadTags();
  } catch (error) {
    ElMessage.error({
      message: "保存失败",
      plain: true,
    });
  }
};

// 删除标签
const deleteTag = async (tag) => {
  try {
    await ElMessageBox.confirm(
      "确定要删除这个标签吗？此操作不可恢复。",
      "警告",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await request(`/api/admin/tags/${tag.id}`, {
      method: "DELETE",
    });

    ElMessage.success({
      message: "删除成功",
      plain: true,
    });
    loadTags();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error({
        message: "删除失败",
        plain: true,
      });
    }
  }
};

// 添加标签到提示词
const addTags = async () => {
  if (!selectedTags.value.length) {
    ElMessage.warning({
      message: "请选择要添加的标签",
      plain: true,
    });
    return;
  }

  try {
    for (const tagId of selectedTags.value) {
      await request(
        `/api/admin/prompts/${selectedPrompt.value.id}/tags/${tagId}`,
        {
          method: "POST",
        }
      );
    }

    ElMessage.success({
      message: "添加标签成功",
      plain: true,
    });
    selectedTags.value = [];
    refreshData();
  } catch (error) {
    ElMessage.error({
      message: "添加标签失败",
      plain: true,
    });
  }
};

// 从提示词移除标签
const removeTag = async (prompt, tag) => {
  try {
    await request(`/api/admin/prompts/${prompt.id}/tags/${tag.id}`, {
      method: "DELETE",
    });

    ElMessage.success({
      message: "移除标签成功",
      plain: true,
    });
    refreshData();
  } catch (error) {
    ElMessage.error({
      message: "移除标签失败",
      plain: true,
    });
  }
};

// 打开设置
const openSettings = async () => {
  try {
    const data = await request("/api/admin/prompt-market/settings");
    settings.value = data;
    dialogVisible.value.settings = true;
  } catch (error) {
    ElMessage.error({
      message: "加载设置失败",
      plain: true,
    });
  }
};

// 保存设置
const saveSettings = async () => {
  try {
    await request("/api/admin/prompt-market/settings", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(settings.value),
    });
    ElMessage.success({
      message: "设置已保存",
      plain: true,
    });
    dialogVisible.value.settings = false;
  } catch (error) {
    ElMessage.error({
      message: "保存设置失败",
      plain: true,
    });
  }
};

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val;
  page.value = 1;
  loadData();
};

const handlePageChange = (val) => {
  page.value = val;
  loadData();
};

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768;
};

onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile);
  loadData();
  loadStats();
  loadTags();
});

onUnmounted(() => {
  window.removeEventListener("resize", checkMobile);
});
</script>

<style scoped>
/* 统计卡片样式 */
.stats-card :deep(.el-card__body) {
  padding: 12px 16px;
}

.stats-card {
  transition: all 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 通用弹窗样式 */
:deep(.el-dialog) {
  margin: 0 auto !important;
  position: relative;
  top: 50%;
  transform: translateY(-50%);
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  padding: 16px;
  margin: 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

:deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.el-dialog__footer) {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* 描述列表样式 */
:deep(.el-descriptions__cell) {
  padding: 12px 16px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: var(--el-text-color-regular);
}

/* 表单组件样式 */
:deep(.el-select) {
  width: 100%;
}

:deep(.el-color-picker) {
  width: 100%;
}

:deep(.el-color-picker__trigger) {
  width: 100%;
  padding: 6px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
}

/* 移动端样式优化 */
@media (max-width: 768px) {
  /* 统计卡片 */
  .stats-card :deep(.el-card__body) {
    padding: 12px;
  }

  /* 弹窗样式 */
  :deep(.el-dialog__body) {
    padding: 15px;
    max-height: 80vh;
  }

  :deep(.el-dialog__header) {
    padding: 15px;
  }

  :deep(.el-dialog__footer) {
    padding: 15px;
  }

  /* 表单样式 */
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }

  :deep(.el-form-item__label) {
    padding-bottom: 4px;
  }

  :deep(.el-input),
  :deep(.el-select),
  :deep(.el-date-picker),
  :deep(.el-input-number) {
    width: 100% !important;
  }

  :deep(.el-input__wrapper) {
    padding: 0 11px;
  }

  :deep(.el-input__inner) {
    height: 36px;
  }

  /* 按钮样式 */
  :deep(.el-button) {
    padding: 8px 16px;
    height: 40px;
  }

  /* 分页样式 */
  .pagination-mobile {
    :deep(.el-pagination__jump) {
      display: none;
    }
  }

  /* 描述列表样式 */
  .descriptions-mobile :deep(.el-descriptions__cell) {
    padding: 8px 12px;
  }
}

/* 桌面端样式 */
@media (min-width: 768px) {
  .stats-card :deep(.el-card__body) {
    padding: 20px;
  }

  :deep(.el-dialog__body) {
    padding: 20px;
  }
}

/* Select 下拉菜单样式 */
:deep(.el-select-dropdown) {
  max-width: 90vw;
}

/* 表格样式优化 */
:deep(.el-table) {
  --el-table-border-color: var(--el-border-color-lighter);
}

:deep(.el-table th) {
  background-color: var(--el-fill-color-light);
  font-weight: 600;
}

:deep(.el-table td) {
  padding: 8px 12px;
}

/* 按钮组样式 */
.button-group {
  display: flex;
  gap: 8px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 详情弹窗样式 */
.detail-dialog :deep(.el-dialog) {
  margin: 0 auto !important;
  position: relative;
  top: 50%;
  transform: translateY(-50%);
  max-height: 90vh;
}

.detail-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: calc(70vh - 120px); /* 减去header和footer的高度 */
  overflow-y: auto;
}
.filter-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 768px) {
  .filter-container {
    flex-direction: row;
    align-items: center;
  }

  /* 桌面端筛选器宽度控制 */
  :deep(.el-select) {
    width: auto !important;
    min-width: 160px;
  }
}

/* 移动端筛选器宽度控制 */
@media (max-width: 767px) {
  :deep(.el-select) {
    width: 100% !important;
  }
}
@media (max-width: 768px) {
  .detail-dialog :deep(.el-dialog__body) {
    padding: 15px;
    max-height: calc(80vh - 110px);
  }
}
</style>
