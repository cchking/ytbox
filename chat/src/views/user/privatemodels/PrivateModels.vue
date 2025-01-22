<!-- src/views/PrivateModels.vue -->
<template>
  <div class="container mx-auto px-4 py-6">
    <!-- 标题和操作栏 -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-xl font-bold">私有模型</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        创建模型
      </el-button>
    </div>

    <!-- 模型列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <el-card
        v-for="model in models"
        :key="model.id"
        class="hover:shadow-lg transition-shadow"
      >
        <div class="flex gap-4">
          <img
            :src="model.icon || '/placeholder.png'"
            class="w-20 h-20 object-cover rounded-lg shrink-0"
            :alt="model.name"
          />
          <div class="flex-1 min-w-0">
            <h3 class="text-lg font-medium mb-2">{{ model.name }}</h3>
            <p class="text-gray-600 text-sm line-clamp-2 mb-2">
              {{ model.description }}
            </p>
            <div class="flex items-center text-xs text-gray-500">
              <Calendar class="w-3.5 h-3.5 mr-1" />
              {{ formatDate(model.created_at) }}
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end gap-2 mt-4">
          <el-button
            type="primary"
            link
            @click="handlePublish(model)"
            class="!p-1"
          >
            发布到市场
          </el-button>
          <el-button
            type="primary"
            link
            @click="handleEdit(model)"
            class="!p-1"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            link
            @click="handleDelete(model)"
            class="!p-1"
          >
            删除
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!models.length" description="暂无私有模型">
      <el-button type="primary" @click="showCreateDialog = true">
        创建模型
      </el-button>
    </el-empty>

    <!-- 创建/编辑对话框 -->
    <private-model-dialog
      v-model="showCreateDialog"
      :model="editingModel"
      @success="handleSuccess"
    />

    <!-- 发布对话框 -->
    <el-dialog
      v-model="showPublishDialog"
      title="发布到市场"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="publishFormRef"
        :model="publishForm"
        :rules="publishRules"
        label-width="120px"
      >
        <div class="bg-gray-50 rounded-lg p-6">
          <el-form-item label="分发方式" prop="distribution_type">
            <div class="flex-1">
              <el-radio-group v-model="publishForm.distribution_type">
                <el-radio-button label="free_pull">免费拉取</el-radio-button>
                <el-radio-button label="coin_pull">金币拉取</el-radio-button>
                <el-radio-button label="key_pull">激活码拉取</el-radio-button>
              </el-radio-group>
              <div class="mt-2 text-xs text-gray-500">
                {{ getDistributionTips(publishForm.distribution_type) }}
              </div>
            </div>
          </el-form-item>

          <el-form-item
            v-if="publishForm.distribution_type === 'coin_pull'"
            label="拉取价格"
            prop="pull_price"
          >
            <el-input-number
              v-model="publishForm.pull_price"
              :min="0"
              :precision="0"
              controls-position="right"
              class="!w-[200px]"
            >
              <template #append>金币</template>
            </el-input-number>
          </el-form-item>

          <el-form-item label="使用方式" prop="usage_type">
            <div class="flex-1">
              <el-radio-group v-model="publishForm.usage_type">
                <el-radio-button label="free">免费使用</el-radio-button>
                <el-radio-button label="coin">付费使用</el-radio-button>
              </el-radio-group>
              <div class="mt-2 text-xs text-gray-500">
                {{ getUsageTips(publishForm.usage_type) }}
              </div>
            </div>
          </el-form-item>

          <el-form-item
            v-if="publishForm.usage_type === 'coin'"
            label="使用价格"
            prop="usage_price"
          >
            <el-input-number
              v-model="publishForm.usage_price"
              :min="0"
              :precision="0"
              controls-position="right"
              class="!w-[200px]"
            >
              <template #append>金币/次</template>
            </el-input-number>
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button @click="showPublishDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="handlePublishSubmit"
            :loading="publishing"
          >
            发布到市场
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from "vue";
import { Calendar } from "lucide-vue-next";
import { ElMessage, ElMessageBox } from "element-plus";
import { request } from "@/utils/request";
import PrivateModelDialog from "./PrivateModelDialog.vue";

const models = ref([]);
const showCreateDialog = ref(false);
const editingModel = ref(null);
const showPublishDialog = ref(false);
const publishing = ref(false);
const publishFormRef = ref(null);
const publishingModel = ref(null);

const publishForm = reactive({
  distribution_type: "free_pull",
  pull_price: 0,
  usage_type: "free",
  usage_price: 0,
});

const publishRules = {
  distribution_type: [
    { required: true, message: "请选择分发方式", trigger: "change" },
  ],
  usage_type: [
    { required: true, message: "请选择使用方式", trigger: "change" },
  ],
  pull_price: [
    {
      required: true,
      message: "请输入拉取价格",
      trigger: "change",
      type: "number",
    },
  ],
  usage_price: [
    {
      required: true,
      message: "请输入使用价格",
      trigger: "change",
      type: "number",
    },
  ],
};

// 加载模型列表
const loadModels = async () => {
  try {
    const data = await request("/api/private-models");
    models.value = data;
  } catch (error) {
    ElMessage.error({
      message: error.response?.data?.detail || "加载失败",
      plain: true,
    });
  }
};

// 处理编辑
const handleEdit = (model) => {
  editingModel.value = model;
  showCreateDialog.value = true;
};

// 处理删除
const handleDelete = async (model) => {
  try {
    await ElMessageBox.confirm(
      "确定要删除这个模型吗？此操作不可恢复。",
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await request(`/api/private-models/${model.id}`, {
      method: "DELETE",
    });

    ElMessage.success({
      message: "删除成功",
      plain: true,
    });
    loadModels();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error({
        message: error.response?.data?.detail || "删除失败",
        plain: true,
      });
    }
  }
};

// 处理创建/编辑成功
const handleSuccess = () => {
  showCreateDialog.value = false;
  editingModel.value = null;
  loadModels();
};

// 处理发布点击
const handlePublish = (model) => {
  publishingModel.value = model;
  showPublishDialog.value = true;
  // 重置表单
  publishForm.distribution_type = "free_pull";
  publishForm.usage_type = "free";
  publishForm.pull_price = 0;
  publishForm.usage_price = 0;
};

// 处理发布提交
const handlePublishSubmit = async () => {
  if (!publishFormRef.value) return;

  await publishFormRef.value.validate(async (valid, fields) => {
    if (!valid) return;

    publishing.value = true;
    try {
      const formData = new FormData();

      // 复制现有模型的基本信息
      formData.append("name", publishingModel.value.name);
      formData.append("description", publishingModel.value.description);
      formData.append("api_base_url", publishingModel.value.api_base_url);
      formData.append("api_key", publishingModel.value.api_key);

      // 添加分发和使用设置
      formData.append("distribution_type", publishForm.distribution_type);
      formData.append("usage_type", publishForm.usage_type);
      formData.append("pull_price", publishForm.pull_price);
      formData.append("usage_price", publishForm.usage_price);

      // 复制图标
      if (publishingModel.value.icon) {
        const iconResponse = await fetch(publishingModel.value.icon);
        const iconBlob = await iconResponse.blob();
        formData.append("icon", iconBlob, "icon.png");
      }

      // 调用发布到市场的接口
      await request(`/api/private-models/${publishingModel.value.id}/publish`, {
        method: "POST",
        body: formData,
      });

      ElMessage.success({
        message: "发布成功",
        plain: true,
      });
      showPublishDialog.value = false;
    } catch (error) {
      ElMessage.error({
        message: error.response?.data?.detail || "发布失败",
        plain: true,
      });
    } finally {
      publishing.value = false;
    }
  });
};

// 提示文本
const getDistributionTips = (type) => {
  const tips = {
    free_pull: "任何用户都可以免费拉取使用",
    coin_pull: "用户需要支付金币才能拉取使用",
    key_pull: "用户需要兑换码才能拉取使用",
  };
  return tips[type] || "";
};

const getUsageTips = (type) => {
  const tips = {
    free: "用户拉取后可以免费使用",
    coin: "用户每次使用都需要支付金币",
  };
  return tips[type] || "";
};

// 格式化日期
const formatDate = (date) => {
  if (!date) return "";
  const d = new Date(date);
  if (isNaN(d.getTime())) return "";

  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

onMounted(() => {
  loadModels();
});
</script>
