<!-- MarketModelsManager.vue -->
<template>
  <div class="p-4 space-y-4">
    <!-- 搜索和筛选栏 -->
    <div class="flex flex-wrap gap-4 mb-6">
      <!-- 模型类型选择器 -->
      <el-select v-model="modelType" class="w-full sm:w-40">
        <el-option label="已创建的" value="created" />
        <el-option label="已购买的" value="pulled" />
      </el-select>

      <!-- 搜索输入框 -->
      <el-input
        v-model="searchQuery"
        placeholder="搜索模型名称或描述"
        class="flex-1"
        clearable
      >
        <template #prefix>
          <Search class="w-4 h-4 text-gray-400" />
        </template>
      </el-input>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <el-loading :visible="true" />
    </div>

    <!-- 空状态 -->
    <div
      v-else-if="filteredModels.length === 0"
      class="flex flex-col items-center justify-center h-64 text-gray-500"
    >
      <Search class="w-12 h-12 mb-4" />
      <p v-if="searchQuery">没有找到匹配的模型</p>
      <p v-else>
        {{ modelType === "created" ? "暂无创建的模型" : "暂无购买的模型" }}
      </p>
    </div>

    <!-- 模型列表 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="model in filteredModels"
        :key="model.id"
        class="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 p-6"
      >
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-lg font-semibold">{{ model.name }}</h3>
          <el-tag
            :type="getStatusTagType(model.status)"
            size="small"
            class="rounded-full px-3"
          >
            {{ getStatusText(model.status) }}
          </el-tag>
        </div>

        <div class="space-y-3 mb-6">
          <!-- 模型图标 -->
          <div v-if="model.icon" class="mb-4">
            <img
              :src="model.icon"
              class="w-16 h-16 object-cover rounded-lg"
              alt="模型图标"
            />
          </div>

          <p class="text-sm text-gray-600 line-clamp-2">
            {{ model.description }}
          </p>
          <div
            class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-500"
          >
            <div class="flex items-center">
              <span class="mr-1">使用类型：</span>
              <span class="font-medium">{{
                getUsageTypeText(model.usage_type)
              }}</span>
            </div>
            <div class="flex items-center">
              <span class="mr-1">分发方式：</span>
              <span class="font-medium">{{
                getDistributionTypeText(model.distribution_type)
              }}</span>
            </div>
          </div>
          <div class="flex items-center text-sm text-gray-500 justify-between">
            <span class="flex items-center">
              <CreditCard class="w-4 h-4 mr-1" />
              拉取价格：{{ model.pull_price }} 金币
            </span>
            <span class="flex items-center">
              <Coins class="w-4 h-4 mr-1" />
              使用价格：{{ model.usage_price }} 金币
            </span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex flex-wrap items-center justify-end gap-2">
          <!-- 仅为创建的模型显示编辑/管理按钮 -->
          <template v-if="modelType === 'created'">
            <el-button
              @click="handleEdit(model)"
              type="primary"
              plain
              size="small"
              class="!flex !items-center"
            >
              <Pencil class="w-4 h-4 mr-1" />编辑
            </el-button>

            <el-button
              v-if="model.distribution_type === 'key_pull'"
              @click="handleManageKeys(model)"
              type="info"
              plain
              size="small"
              class="!flex !items-center"
            >
              <Key class="w-4 h-4 mr-1" />兑换码
            </el-button>

            <el-button
              v-if="model.status === 'delisted'"
              @click="confirmRelist(model.id)"
              type="success"
              plain
              size="small"
              class="!flex !items-center"
            >
              <ArrowUpToLine class="w-4 h-4 mr-1" />上架
            </el-button>
            <el-button
              v-else
              @click="confirmDelist(model.id)"
              type="danger"
              plain
              size="small"
              class="!flex !items-center"
            >
              <ArrowDownToLine class="w-4 h-4 mr-1" />下架
            </el-button>
          </template>

          <!-- 为已购买的模型显示使用按钮 -->
          <el-button
            v-else
            @click="handleUseModel(model)"
            type="primary"
            size="small"
            class="!flex !items-center"
          >
            <PlayCircle class="w-4 h-4 mr-1" />使用模型
          </el-button>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑模型"
      class="custom-dialog"
      :append-to-body="true"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      @close="handleDialogClose"
    >
      <el-form :model="editModel" label-width="100px" class="px-2">
        <el-form-item label="名称" class="mb-6">
          <el-input v-model="editModel.name" placeholder="请输入模型名称" />
        </el-form-item>

        <!-- 图标上传 -->
        <el-form-item label="图标" class="mb-6">
          <div class="flex items-center gap-4">
            <img
              v-if="editModel.icon"
              :src="editModel.icon"
              class="w-16 h-16 object-cover rounded-lg"
              alt="模型图标"
            />
            <el-upload
              class="flex-1"
              accept="image/*"
              :show-file-list="false"
              :before-upload="handleIconUpload"
            >
              <el-button type="primary" plain>
                {{ editModel.icon ? "更换图标" : "上传图标" }}
              </el-button>
            </el-upload>
          </div>
        </el-form-item>

        <el-form-item label="描述" class="mb-6">
          <el-input
            v-model="editModel.description"
            type="textarea"
            rows="3"
            placeholder="请输入模型描述"
          />
        </el-form-item>

        <el-form-item label="分发方式" class="mb-6">
          <el-select v-model="editModel.distribution_type" class="w-full">
            <el-option label="免费拉取" value="free_pull" />
            <el-option label="付费拉取" value="coin_pull" />
            <el-option label="密钥拉取" value="key_pull" />
          </el-select>
        </el-form-item>

        <el-form-item label="使用类型" class="mb-6">
          <el-select v-model="editModel.usage_type" class="w-full">
            <el-option label="免费使用" value="free" />
            <el-option label="付费使用" value="coin" />
          </el-select>
        </el-form-item>

        <el-form-item
          v-if="editModel.distribution_type === 'coin_pull'"
          label="拉取价格"
          class="mb-6"
        >
          <el-input-number
            v-model="editModel.pull_price"
            :min="0"
            class="w-full"
          />
        </el-form-item>

        <el-form-item
          v-if="editModel.usage_type === 'coin'"
          label="使用价格"
          class="mb-6"
        >
          <el-input-number
            v-model="editModel.usage_price"
            :min="0"
            class="w-full"
          />
        </el-form-item>

        <el-form-item label="API地址" class="mb-6">
          <el-input
            v-model="editModel.api_base_url"
            placeholder="请输入API地址"
          />
        </el-form-item>

        <el-form-item label="API密钥" class="mb-6">
          <el-input
            v-model="editModel.api_key"
            show-password
            placeholder="请输入API密钥"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 兑换码管理弹窗 -->
    <el-dialog
      v-model="showKeysDialog"
      title="兑换码管理"
      class="custom-dialog keys-dialog"
      :append-to-body="true"
      :close-on-click-modal="false"
      :destroy-on-close="true"
    >
      <div class="flex justify-between items-center flex-wrap gap-2 mb-4">
        <div class="flex gap-2">
          <el-button
            type="primary"
            @click="showGenerateKeysDialog"
            class="!flex !items-center"
          >
            <Plus class="w-4 h-4 mr-1" />生成兑换码
          </el-button>
        </div>

        <el-input
          v-model="searchKey"
          placeholder="搜索兑换码"
          class="!w-full sm:!w-64"
          clearable
        >
          <template #prefix>
            <Search class="w-4 h-4 text-gray-400" />
          </template>
        </el-input>
      </div>

      <el-table :data="filteredKeys" stripe class="w-full" :max-height="400">
        <el-table-column label="兑换码" min-width="120">
          <template #default="scope">
            <div class="flex items-center gap-2">
              <span class="flex-1">{{ scope.row.key_code }}</span>
              <el-button
                type="primary"
                link
                size="small"
                @click="copyKeyCode(scope.row.key_code)"
                class="!flex !items-center shrink-0"
              >
                <Copy class="w-4 h-4" />
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="used_by" label="使用状态" width="120">
          <template #default="scope">
            <el-tag
              :type="scope.row.used_by ? 'success' : 'info'"
              class="rounded-full"
            >
              {{ scope.row.used_by ? "已使用" : "未使用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button
              type="danger"
              link
              @click="confirmDeleteKey(scope.row.id)"
              class="!flex !items-center"
            >
              <Trash2 class="w-4 h-4 mr-1" />删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="totalKeys > 0"
        class="mt-4 flex justify-center"
        :current-page="currentPage"
        :page-size="pageSize"
        :total="totalKeys"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </el-dialog>

    <!-- 生成兑换码弹窗 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="生成兑换码"
      class="custom-dialog generate-dialog"
      :append-to-body="true"
      :close-on-click-modal="false"
      :destroy-on-close="true"
    >
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="生成数量">
          <el-input-number
            v-model="generateForm.count"
            :min="1"
            :max="100"
            class="w-full"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="showGenerateDialog = false">取消</el-button>
          <el-button type="primary" @click="handleGenerateKeys">生成</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, computed, watch, onMounted } from "vue";
import {
  Key,
  Pencil,
  ArrowUpToLine,
  ArrowDownToLine,
  Plus,
  Trash2,
  CreditCard,
  Coins,
  Search,
  Copy,
  PlayCircle,
} from "lucide-vue-next";
import { ElMessage, ElMessageBox } from "element-plus";
import { request } from "@/utils/request";
import { useRouter } from "vue-router";

const router = useRouter();

// 状态变量
const models = ref([]);
const loading = ref(true);
const showEditDialog = ref(false);
const showKeysDialog = ref(false);
const showGenerateDialog = ref(false);
const editModel = ref(null);
const currentModelId = ref(null);
const modelKeys = ref([]);
const totalKeys = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const generateForm = ref({ count: 1 });
const searchKey = ref("");
const modelType = ref("created"); // 'created' 或 'pulled'
const searchQuery = ref("");

// 计算属性：过滤后的模型列表
const filteredModels = computed(() => {
  if (!searchQuery.value) return models.value;

  const query = searchQuery.value.toLowerCase();
  return models.value.filter(
    (model) =>
      model.name.toLowerCase().includes(query) ||
      (model.description && model.description.toLowerCase().includes(query))
  );
});

// 计算属性：过滤后的兑换码列表
const filteredKeys = computed(() => {
  if (!searchKey.value) return modelKeys.value;
  const keyword = searchKey.value.toLowerCase();
  return modelKeys.value.filter((key) =>
    key.key_code.toLowerCase().includes(keyword)
  );
});

// 复制兑换码
const copyKeyCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code);
    ElMessage({
      message: "复制成功",
      type: "success",
      plain: true,
    });
  } catch (err) {
    ElMessage({
      message: "复制失败",
      type: "error",
      plain: true,
    });
  }
};

// 格式化日期
const formatDate = (date) => {
  if (!date) return "";
  return new Date(date).toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
};

// 状态文本映射
const getStatusText = (status) => {
  const statusMap = {
    approved: "已通过",
    pending: "待审核",
    rejected: "已拒绝",
    delisted: "已下架",
  };
  return statusMap[status] || status;
};

// 使用类型文本映射
const getUsageTypeText = (type) => {
  const typeMap = {
    free: "免费使用",
    coin: "付费使用",
  };
  return typeMap[type] || type;
};

// 分发方式文本映射
const getDistributionTypeText = (type) => {
  const typeMap = {
    free_pull: "免费拉取",
    coin_pull: "付费拉取",
    key_pull: "密钥拉取",
  };
  return typeMap[type] || type;
};

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    approved: "success",
    pending: "warning",
    rejected: "danger",
    delisted: "info",
  };
  return typeMap[status] || "info";
};

// 图标上传处理
const handleIconUpload = (file) => {
  const allowedTypes = [
    "image/jpeg",
    "image/png",
    "image/svg+xml",
    "application/svg+xml",
  ];

  const isValidType = allowedTypes.includes(file.type);
  if (!isValidType) {
    ElMessage.error("只支持 JPG、PNG 或 SVG 格式的图片");
    return false;
  }

  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    ElMessage.error("图片大小不能超过 2MB!");
    return false;
  }

  editModel.value.iconFile = file;
  editModel.value.icon = URL.createObjectURL(file);

  return false;
};

// 获取模型列表
const fetchModels = async () => {
  try {
    loading.value = true;
    const data = await request(
      `/api/market/user/models?type=${modelType.value}`
    );
    models.value = data;
  } catch (err) {
    ElMessage({
      message:
        err.message ||
        `获取${modelType.value === "created" ? "创建" : "购买"}的模型列表失败`,
      type: "error",
      plain: true,
    });
  } finally {
    loading.value = false;
  }
};

// 获取模型兑换码列表
const fetchModelKeys = async () => {
  try {
    if (!currentModelId.value) return;
    const data = await request(
      `/api/market/models/${currentModelId.value}/keys?page=${currentPage.value}&page_size=${pageSize.value}`
    );
    modelKeys.value = data.items;
    totalKeys.value = data.total;
  } catch (err) {
    ElMessage({
      message: err.message || "获取兑换码列表失败",
      type: "error",
      plain: true,
    });
  }
};

// 编辑模型
const handleEdit = (model) => {
  editModel.value = {
    ...model,
    iconFile: null,
  };
  showEditDialog.value = true;
};

// 管理兑换码
const handleManageKeys = async (model) => {
  currentModelId.value = model.id;
  currentPage.value = 1;
  showKeysDialog.value = true;
  await fetchModelKeys();
};

// 使用模型
const handleUseModel = (model) => {
  // 导航到聊天界面并使用选定的模型
  router.push({
    name: "chat",
    query: { model: model.name },
  });
};

// 显示生成兑换码对话框
const showGenerateKeysDialog = () => {
  generateForm.value.count = 1;
  showGenerateDialog.value = true;
};

// 生成兑换码
const handleGenerateKeys = async () => {
  try {
    await request(`/api/market/models/${currentModelId.value}/keys/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(generateForm.value),
    });

    ElMessage({
      message: "兑换码生成成功",
      type: "success",
      plain: true,
    });
    showGenerateDialog.value = false;
    await fetchModelKeys();
  } catch (err) {
    ElMessage({
      message: err.message || "生成兑换码失败",
      type: "error",
      plain: true,
    });
  }
};

// 确认删除兑换码
const confirmDeleteKey = async (keyId) => {
  try {
    await ElMessageBox.confirm("确定要删除这个兑换码吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
      customClass: "custom-message-box",
    });

    await request(`/api/market/models/${currentModelId.value}/keys/${keyId}`, {
      method: "DELETE",
    });

    ElMessage({
      message: "兑换码删除成功",
      type: "success",
      plain: true,
    });
    await fetchModelKeys();
  } catch (err) {
    if (err !== "cancel") {
      ElMessage({
        message: err.message || "删除兑换码失败",
        type: "error",
        plain: true,
      });
    }
  }
};

// 确认上架
const confirmRelist = async (modelId) => {
  try {
    await ElMessageBox.confirm("确定要重新上架这个模型吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
      customClass: "custom-message-box",
    });

    await request(`/api/market/models/${modelId}/list`, {
      method: "POST",
    });

    ElMessage({
      message: "模型已成功上架",
      type: "success",
      plain: true,
    });
    await fetchModels();
  } catch (err) {
    if (err !== "cancel") {
      ElMessage({
        message: err.message || "上架模型失败",
        type: "error",
        plain: true,
      });
    }
  }
};

// 确认下架
const confirmDelist = async (modelId) => {
  try {
    await ElMessageBox.confirm("确定要下架这个模型吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
      customClass: "custom-message-box",
    });

    await request(`/api/market/models/${modelId}/delist`, {
      method: "POST",
    });

    ElMessage({
      message: "模型已成功下架",
      type: "success",
      plain: true,
    });
    await fetchModels();
  } catch (err) {
    if (err !== "cancel") {
      ElMessage({
        message: err.message || "下架模型失败",
        type: "error",
        plain: true,
      });
    }
  }
};

// 保存修改
const handleSave = async () => {
  try {
    const formData = new FormData();

    // 添加其他字段，但排除 icon 和 iconFile 字段
    Object.keys(editModel.value).forEach((key) => {
      if (
        key !== "iconFile" &&
        key !== "icon" &&
        editModel.value[key] !== null &&
        editModel.value[key] !== undefined
      ) {
        formData.append(key, editModel.value[key]);
      }
    });

    // 只有当有新上传的图标文件时才添加到 FormData
    if (editModel.value.iconFile) {
      formData.append("icon", editModel.value.iconFile);
    }

    await request(`/api/market/models/${editModel.value.id}`, {
      method: "PUT",
      body: formData,
    });

    showEditDialog.value = false;
    ElMessage({
      message: "模型更新成功",
      type: "success",
      plain: true,
    });
    await fetchModels();
  } catch (err) {
    ElMessage({
      message: err.message || "更新模型失败",
      type: "error",
      plain: true,
    });
  }
};

// 对话框关闭处理
const handleDialogClose = () => {
  editModel.value = null;
};

// 分页变化处理
const handlePageChange = async (page) => {
  currentPage.value = page;
  await fetchModelKeys();
};

// 观察模型类型变化
watch(modelType, () => {
  fetchModels();
});

// 生命周期钩子
onMounted(() => {
  fetchModels();
});
</script>

<style>
/* 弹窗容器样式 */
.el-overlay-dialog {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 弹窗本体样式 */
.el-dialog {
  --dialog-border-radius: 32px;
  border-radius: var(--dialog-border-radius) !important;
  margin: 15vh auto !important;
  width: min(800px, 95%) !important;
  max-height: 90vh;
}

/* 恢复其他样式 */
.el-button {
  border-radius: 12px !important;
}

.bg-white.rounded-xl {
  border-radius: 32px !important;
}

.el-input__wrapper,
.el-textarea__inner {
  border-radius: 16px !important;
}

/* 移动端适配 */
@media (max-width: 640px) {
  .el-dialog {
    width: 92% !important;
    max-height: 92vh !important;
  }

  .el-dialog__body {
    padding: 20px !important;
  }
}
</style>
