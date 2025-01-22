<!-- src/views/components/PrivateModelDialog.vue -->
<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑模型' : '创建模型'"
    :width="windowWidth <= 640 ? '90%' : '800px'"
    :close-on-click-modal="false"
    @closed="handleClosed"
    class="private-model-dialog"
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
                    class="w-[140px] h-[140px] sm:w-[178px] sm:h-[178px] object-cover rounded-lg"
                  />
                  <div
                    v-else
                    class="w-[140px] h-[140px] sm:w-[178px] sm:h-[178px] flex flex-col items-center justify-center text-gray-400"
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
      </el-form>
    </el-scrollbar>

    <template #footer>
      <div class="flex justify-end gap-2">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? "保存" : "创建" }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from "vue";
import { PlusCircle } from "lucide-vue-next";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";

const props = defineProps({
  modelValue: Boolean,
  model: Object,
});

const emit = defineEmits(["update:modelValue", "success"]);

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

// 添加窗口宽度响应式
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

const isEdit = computed(() => !!props.model);

const formRef = ref(null);
const submitting = ref(false);
const iconFile = ref(null);
const previewIcon = ref(null);
const apiProtocol = ref("https://");

const modelForm = reactive({
  name: "",
  description: "",
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

// 图标处理
const handleIconChange = (file) => {
  const isImage =
    file.raw.type === "image/jpeg" ||
    file.raw.type === "image/png" ||
    file.raw.type === "image/svg+xml" ||
    file.raw.type === "application/svg+xml"; // 某些浏览器可能使用这个 MIME 类型
  const isLt2M = file.raw.size / 1024 / 1024 < 2;

  if (!isImage) {
    ElMessage({
      message: "图标只能是 JPG、PNG 或 SVG 格式!", // 更新错误提示信息
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

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid, fields) => {
    if (!valid) return;

    submitting.value = true;
    try {
      const formData = new FormData();
      formData.append("name", modelForm.name);
      formData.append("description", modelForm.description);
      formData.append(
        "api_base_url",
        `${apiProtocol.value}${modelForm.api_base_url}`
      );
      formData.append("api_key", modelForm.api_key);

      if (iconFile.value) {
        formData.append("icon", iconFile.value);
      }

      if (isEdit.value) {
        await request(`/api/private-models/${props.model.id}`, {
          method: "PUT",
          body: formData,
        });
        ElMessage({
          message: "更新成功",
          type: "success",
          plain: true,
        });
      } else {
        await request("/api/private-models", {
          method: "POST",
          body: formData,
        });
        ElMessage({
          message: "创建成功",
          type: "success",
          plain: true,
        });
      }

      dialogVisible.value = false;
      emit("success");
    } catch (error) {
      ElMessage({
        message:
          error.response?.data?.detail ||
          (isEdit.value ? "更新失败" : "创建失败"),
        type: "error",
        plain: true,
      });
    } finally {
      submitting.value = false;
    }
  });
};

// 关闭时重置
const handleClosed = () => {
  formRef.value?.resetFields();
  iconFile.value = null;
  previewIcon.value = null;
  apiProtocol.value = "https://";
  if (previewIcon.value) {
    URL.revokeObjectURL(previewIcon.value);
  }
};

// 监听编辑模型变化
watch(
  () => props.model,
  (newModel) => {
    if (newModel) {
      // 如果是编辑模式，填充表单数据
      const url = newModel.api_base_url || "";
      const protocolMatch = url.match(/^(https?:\/\/)/);
      if (protocolMatch) {
        apiProtocol.value = protocolMatch[1];
        modelForm.api_base_url = url.replace(protocolMatch[1], "");
      } else {
        modelForm.api_base_url = url;
      }

      modelForm.name = newModel.name;
      modelForm.description = newModel.description;
      modelForm.api_key = newModel.api_key;

      if (newModel.icon) {
        previewIcon.value = newModel.icon;
      }
    } else {
      // 如果不是编辑模式，重置表单
      handleClosed();
    }
  },
  { immediate: true }
);

// 组件卸载时清理资源
onUnmounted(() => {
  if (previewIcon.value) {
    URL.revokeObjectURL(previewIcon.value);
  }
});
</script>

<style>
.private-model-dialog :deep(.el-form-item__content) {
  flex: 1;
  min-width: 0;
}

.private-model-dialog :deep(.el-dialog__body) {
  padding: 20px 0;
}

.private-model-dialog :deep(.el-dialog__header) {
  margin: 0;
  padding: 20px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.private-model-dialog :deep(.el-dialog__footer) {
  margin: 0;
  padding: 20px 24px;
  border-top: 1px solid var(--el-border-color-lighter);
}

@media screen and (max-width: 640px) {
  .private-model-dialog {
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

    :deep(.el-input-number) {
      width: 100% !important;
    }

    :deep(.el-select) {
      width: 100%;
    }

    :deep(.el-input__wrapper) {
      width: 100%;
    }

    /* 协议选择器响应式处理 */
    :deep(.el-input-group__prepend) {
      .el-select {
        width: 90px !important;
      }
    }
  }
}
</style>
