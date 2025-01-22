#src\views\user\modelmarket\PublishDialog.vue
<template>
  <el-dialog
    v-model="dialogVisible"
    title="发布模型"
    :width="windowWidth <= 640 ? '90%' : '800px'"
    :close-on-click-modal="false"
    @closed="handleClosed"
    class="publish-model-dialog"
  >
    <el-scrollbar max-height="calc(90vh - 200px)">
      <el-form
        ref="formRef"
        :model="modelForm"
        :rules="rules"
        :label-width="windowWidth <= 640 ? 'auto' : '120px'"
        :label-position="windowWidth <= 640 ? 'top' : 'right'"
        class="px-5"
      >
        <!-- 基本信息 -->
        <div class="mb-8">
          <div class="text-base font-medium mb-5">基本信息</div>
          <div class="bg-gray-50 rounded-lg p-6">
            <el-form-item label="模型名称" prop="name">
              <el-input v-model="modelForm.name" placeholder="请输入模型名称" />
            </el-form-item>

            <el-form-item label="模型描述" prop="description">
              <el-input
                v-model="modelForm.description"
                type="textarea"
                :rows="4"
                placeholder="请详细描述模型的功能、特点和适用场景"
              />
            </el-form-item>

            <el-form-item label="模型图标">
              <div class="flex flex-col items-start">
                <el-upload
                  class="border-2 border-dashed border-gray-300 rounded-lg cursor-pointer overflow-hidden transition-colors hover:border-primary"
                  :class="previewIcon ? 'border-none' : ''"
                  :action="null"
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handleIconChange"
                >
                  <img
                    v-if="previewIcon"
                    :src="previewIcon"
                    class="w-[178px] h-[178px] object-cover rounded-lg sm:w-[178px] sm:h-[178px] w-[140px] h-[140px]"
                  />
                  <div
                    v-else
                    class="w-[178px] h-[178px] flex flex-col items-center justify-center text-gray-400 sm:w-[178px] sm:h-[178px] w-[140px] h-[140px]"
                  >
                    <PlusCircle class="w-8 h-8 mb-2" />
                    <span class="text-sm">点击上传图标</span>
                  </div>
                </el-upload>
                <div class="mt-2 text-xs text-gray-500">
                  支持 jpg、png、svg(推荐) 格式，建议尺寸 200x200
                </div>
              </div>
            </el-form-item>
          </div>
        </div>

        <!-- API 配置 -->
        <div class="mb-8">
          <div class="text-base font-medium mb-5">API 配置</div>
          <div class="bg-gray-50 rounded-lg p-6">
            <el-form-item label="API 基础地址" prop="api_base_url">
              <div class="flex-1">
                <el-input
                  v-model="modelForm.api_base_url"
                  placeholder="例如: api.example.com/v1"
                >
                  <template #prepend>
                    <el-select v-model="apiProtocol" style="width: 100px">
                      <el-option label="http://" value="http://" />
                      <el-option label="https://" value="https://" />
                    </el-select>
                  </template>
                </el-input>
                <div class="mt-2 text-xs text-gray-500">
                  请输入不含协议头的 API 基础地址
                </div>
              </div>
            </el-form-item>

            <el-form-item label="API Key" prop="api_key">
              <div class="flex-1">
                <el-input
                  v-model="modelForm.api_key"
                  placeholder="请输入 API Key"
                  show-password
                />
                <div class="mt-2 text-xs text-gray-500">
                  此 API Key 将用于调用模型接口
                </div>
              </div>
            </el-form-item>
          </div>
        </div>

        <!-- 访问控制 -->
        <div class="mb-8">
          <div class="text-base font-medium mb-5">访问控制</div>
          <div class="bg-gray-50 rounded-lg p-6">
            <el-form-item label="分发方式" prop="distribution_type">
              <div class="flex-1">
                <el-radio-group v-model="modelForm.distribution_type">
                  <el-radio-button label="free_pull">免费拉取</el-radio-button>
                  <el-radio-button label="coin_pull">金币拉取</el-radio-button>
                  <el-radio-button label="key_pull">激活码拉取</el-radio-button>
                </el-radio-group>
                <div class="mt-2 text-xs text-gray-500">
                  {{ getDistributionTips(modelForm.distribution_type) }}
                </div>
              </div>
            </el-form-item>

            <el-form-item
              v-if="modelForm.distribution_type === 'coin_pull'"
              label="拉取价格"
              prop="pull_price"
            >
              <el-input-number
                v-model="modelForm.pull_price"
                :min="0"
                :precision="0"
                controls-position="right"
                class="!w-full sm:!w-[200px]"
              >
                <template #append>金币</template>
              </el-input-number>
            </el-form-item>

            <el-form-item label="使用方式" prop="usage_type">
              <div class="flex-1">
                <el-radio-group v-model="modelForm.usage_type">
                  <el-radio-button label="free">免费使用</el-radio-button>
                  <el-radio-button label="coin">付费使用</el-radio-button>
                </el-radio-group>
                <div class="mt-2 text-xs text-gray-500">
                  {{ getUsageTips(modelForm.usage_type) }}
                </div>
              </div>
            </el-form-item>

            <el-form-item
              v-if="modelForm.usage_type === 'coin'"
              label="使用价格"
              prop="usage_price"
            >
              <el-input-number
                v-model="modelForm.usage_price"
                :min="0"
                :precision="0"
                controls-position="right"
                class="!w-full sm:!w-[200px]"
              >
                <template #append>金币/次</template>
              </el-input-number>
            </el-form-item>
          </div>
        </div>
      </el-form>
    </el-scrollbar>

    <template #footer>
      <div class="flex justify-end gap-2">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePublish" :loading="publishing">
          发布模型
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from "vue";
import { PlusCircle } from "lucide-vue-next";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue", "published"]);

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const windowWidth = ref(window.innerWidth);

const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(() => {
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
});

const formRef = ref(null);
const publishing = ref(false);
const iconFile = ref(null);
const previewIcon = ref(null);
const apiProtocol = ref("https://");

const modelForm = reactive({
  name: "",
  description: "",
  distribution_type: "free_pull",
  pull_price: 0,
  usage_type: "free",
  usage_price: 0,
  api_base_url: "",
  api_key: "",
});

const rules = {
  name: [
    { required: true, message: "请输入模型名称", trigger: "blur" },
    { min: 1, max: 50, message: "长度在 1 到 50 个字符", trigger: "blur" },
  ],
  description: [
    { required: true, message: "请输入模型描述", trigger: "blur" },
    { min: 1, max: 500, message: "长度在 1 到 500 个字符", trigger: "blur" },
  ],
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
  api_base_url: [
    { required: true, message: "请输入 API 基础地址", trigger: "blur" },
    {
      pattern: /^[^\/].*[^\/]$/,
      message: "请输入正确的 API 地址，不要包含协议头和结尾的斜杠",
      trigger: "blur",
    },
  ],
  api_key: [{ required: true, message: "请输入 API Key", trigger: "blur" }],
};

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

const handleIconChange = async (file) => {
  const isImage =
    file.raw.type === "image/jpeg" ||
    file.raw.type === "image/png" ||
    file.raw.type === "image/svg+xml" ||
    file.raw.type === "application/svg+xml"; // 某些浏览器可能使用这个 MIME 类型
  const isLt2M = file.raw.size / 1024 / 1024 < 2;

  if (!isImage) {
    ElMessage({
      message: "图标只能是 JPG、PNG 或 SVG 格式!",
      type: "error",
      plain: true,
    });
    return;
  }
  if (!isLt2M) {
    ElMessage({
      message: "图标大小不能超过 2MB!",
      type: "error",
      plain: true,
    });
    return;
  }

  iconFile.value = file.raw;
  previewIcon.value = URL.createObjectURL(file.raw);
};

const handlePublish = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid, fields) => {
    if (!valid) return;

    publishing.value = true;
    try {
      const formData = new FormData();

      formData.append("name", modelForm.name);
      formData.append("description", modelForm.description);
      formData.append("distribution_type", modelForm.distribution_type);
      formData.append("usage_type", modelForm.usage_type);
      formData.append("pull_price", modelForm.pull_price);
      formData.append("usage_price", modelForm.usage_price);
      formData.append(
        "api_base_url",
        `${apiProtocol.value}${modelForm.api_base_url}`
      );
      formData.append("api_key", modelForm.api_key);

      if (iconFile.value) {
        formData.append("icon", iconFile.value);
      }

      await request("/api/market/models", {
        method: "POST",
        body: formData,
      });

      ElMessage({
        message: "模型发布成功",
        type: "success",
        plain: true,
      });
      dialogVisible.value = false;
      emit("published");
    } catch (error) {
      console.error("发布失败:", error);
      ElMessage({
        message: error.response?.data?.detail || "发布失败",
        type: "error",
        plain: true,
      });
    } finally {
      publishing.value = false;
    }
  });
};

const handleClosed = () => {
  formRef.value?.resetFields();
  iconFile.value = null;
  previewIcon.value = null;
  apiProtocol.value = "https://";
  if (previewIcon.value) {
    URL.revokeObjectURL(previewIcon.value);
  }
};

onUnmounted(() => {
  if (previewIcon.value) {
    URL.revokeObjectURL(previewIcon.value);
  }
});
</script>

<style>
.publish-model-dialog :deep(.el-form-item__content) {
  flex: 1;
  min-width: 0;
}

.publish-model-dialog :deep(.el-input-number .el-input__wrapper) {
  padding-right: 0;
}

.publish-model-dialog :deep(.el-dialog__body) {
  padding: 20px 0;
}

.publish-model-dialog :deep(.el-dialog__header) {
  margin: 0;
  padding: 20px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.publish-model-dialog :deep(.el-dialog__footer) {
  margin: 0;
  padding: 20px 24px;
  border-top: 1px solid var(--el-border-color-lighter);
}

@media screen and (max-width: 640px) {
  .publish-model-dialog {
    :deep(.el-dialog) {
      width: 90% !important;
      margin: 0 auto !important;
      max-width: none !important;
    }

    :deep(.el-dialog__header) {
      padding: 16px 20px;
    }

    :deep(.el-dialog__footer) {
      padding: 16px 20px;
    }

    :deep(.el-form--label-top .el-form-item__label) {
      margin-bottom: 4px;
    }

    .el-form {
      padding-left: 16px !important;
      padding-right: 16px !important;
    }

    .bg-gray-50 {
      padding: 16px !important;
    }

    .mb-8 {
      margin-bottom: 20px !important;
    }

    .el-upload {
      .w-[178px] {
        width: 140px !important;
      }
      .h-[178px] {
        height: 140px !important;
      }
    }

    :deep(.el-radio-group) {
      display: flex;
      flex-direction: column;
      gap: 8px;
      width: 100%;

      .el-radio-button {
        &__inner {
          width: 100%;
          border-radius: 0;
          border: 1px solid var(--el-border-color);
        }

        &:first-child .el-radio-button__inner {
          border-radius: 4px 4px 0 0;
        }

        &:last-child .el-radio-button__inner {
          border-radius: 0 0 4px 4px;
        }

        .el-radio-button__inner {
          width: 100%;
        }
      }
    }

    :deep(.el-select) {
      width: 100%;
    }

    :deep(.el-input-number) {
      width: 100% !important;
    }
  }
}
</style>
