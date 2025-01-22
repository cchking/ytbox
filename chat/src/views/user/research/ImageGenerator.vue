<!-- ImageGenerator.vue -->
<template>
  <div class="min-h-screen bg-gray-50/50 pb-8">
    <div class="max-w-5xl mx-auto px-4 pt-6">
      <!-- 标签页 -->
      <el-tabs
        v-model="activeTab"
        class="bg-white rounded-xl shadow-sm border border-gray-100"
      >
        <!-- 生成图片标签页 -->
        <el-tab-pane label="生成图片" name="generate">
          <div class="px-8 py-6">
            <div class="flex items-center gap-3 mb-8">
              <div class="w-1 h-8 bg-blue-500 rounded-full"></div>
              <h2 class="text-2xl font-bold text-gray-800">AI 图片生成</h2>
            </div>

            <!-- 主要内容分为左右两栏 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <!-- 左侧表单区域 -->
              <div>
                <el-form
                  :model="formData"
                  :rules="rules"
                  ref="formRef"
                  label-position="top"
                  @submit.prevent="generateImage"
                  class="space-y-6"
                >
                  <!-- 模型和尺寸选择 -->
                  <div class="grid grid-cols-2 gap-4">
                    <el-form-item label="选择模型" prop="model" class="mb-0">
                      <el-select
                        v-model="formData.model"
                        placeholder="请选择模型"
                        class="w-full"
                      >
                        <el-option
                          v-for="option in modelOptions"
                          :key="option.value"
                          :label="option.label"
                          :value="option.value"
                        />
                      </el-select>
                    </el-form-item>

                    <el-form-item label="图片尺寸" prop="size" class="mb-0">
                      <el-select
                        v-model="formData.size"
                        placeholder="请选择尺寸"
                        class="w-full"
                      >
                        <el-option
                          v-for="option in sizeOptions"
                          :key="option.value"
                          :label="option.label"
                          :value="option.value"
                        />
                      </el-select>
                    </el-form-item>
                  </div>

                  <!-- 提示词输入框 -->
                  <el-form-item label="提示词描述" prop="prompt" class="mb-0">
                    <el-input
                      v-model="formData.prompt"
                      type="textarea"
                      :rows="6"
                      placeholder="请详细描述您想要生成的图片内容..."
                      resize="none"
                      class="!bg-gray-50"
                    />
                    <div class="mt-2 text-xs text-gray-500">
                      提示：描述越详细，生成的图片越符合预期
                    </div>
                  </el-form-item>

                  <!-- 高级参数设置区域 -->
                  <div
                    class="bg-gray-50/50 rounded-xl p-6 space-y-4 border border-gray-100"
                  >
                    <h3 class="font-medium text-gray-700">高级参数设置</h3>
                    <!-- 这里可以添加更多的参数设置，比如负面提示词、采样步数等 -->
                  </div>

                  <!-- 错误提示 -->
                  <el-alert
                    v-if="error"
                    :title="error"
                    type="error"
                    show-icon
                  />

                  <!-- 生成按钮 -->
                  <el-button
                    type="primary"
                    :loading="loading"
                    class="w-full !h-12 text-base"
                    @click="generateImage"
                  >
                    {{ loading ? "图片生成中..." : "开始生成" }}
                  </el-button>
                </el-form>
              </div>

              <!-- 右侧预览区域 -->
              <div class="space-y-6">
                <!-- 生成结果展示 -->
                <div
                  v-if="generatedImage"
                  class="bg-white rounded-lg shadow-sm p-4 border border-gray-100"
                >
                  <h3 class="font-medium text-gray-700 mb-4">生成结果</h3>
                  <img
                    :src="generatedImage"
                    alt="生成的图片"
                    class="w-full rounded-lg object-cover"
                  />
                  <div class="flex justify-end mt-4">
                    <el-button type="primary" @click="downloadImage">
                      下载图片
                    </el-button>
                  </div>
                </div>

                <!-- 生成中状态展示 -->
                <div v-if="loading" class="bg-blue-50 rounded-lg p-6">
                  <div class="flex items-center gap-3 mb-4">
                    <el-icon class="text-blue-500"><Loading /></el-icon>
                    <span class="font-medium text-blue-700"
                      >正在生成您的图片，请稍候...</span
                    >
                  </div>
                  <el-progress :percentage="50" :stroke-width="10" />
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 历史记录标签页 -->
        <el-tab-pane label="历史记录" name="history">
          <div class="px-8 py-6">
            <div class="flex items-center justify-between mb-8">
              <div class="flex items-center gap-3">
                <div class="w-1 h-8 bg-blue-500 rounded-full"></div>
                <h2 class="text-2xl font-bold text-gray-800">生成历史</h2>
              </div>

              <!-- 分页控制 -->
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :total="total"
                :page-sizes="[10, 20, 30, 50]"
                layout="total, sizes, prev, pager, next"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                background
                class="!m-0"
              />
            </div>

            <!-- 历史记录网格布局 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <el-empty
                v-if="logs.length === 0"
                description="暂无生成记录"
                class="col-span-2"
              />

              <div
                v-for="log in logs"
                :key="log.id"
                class="bg-white rounded-lg shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow"
              >
                <!-- 记录头部信息 -->
                <div class="flex justify-between items-start mb-4">
                  <div class="space-y-2">
                    <div class="flex items-center gap-2">
                      <span class="font-medium">模型:</span>
                      <el-tag size="small">{{ log.model }}</el-tag>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="font-medium">尺寸:</span>
                      <el-tag size="small" type="success">{{
                        log.size
                      }}</el-tag>
                    </div>
                  </div>
                  <span class="text-sm text-gray-500">
                    {{ formatDate(log.created_at) }}
                  </span>
                </div>

                <!-- 提示词 -->
                <div
                  class="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 mb-4"
                >
                  {{ log.prompt }}
                </div>

                <!-- 图片展示 -->
                <div class="relative group">
                  <img
                    v-if="log.image_url"
                    :src="log.image_url"
                    :alt="log.prompt"
                    class="w-full aspect-square object-cover rounded-lg"
                  />
                  <div
                    class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity flex items-center justify-center opacity-0 group-hover:opacity-100"
                  >
                    <el-button type="primary">查看大图</el-button>
                  </div>
                </div>

                <!-- 错误信息 -->
                <el-alert
                  v-if="log.error"
                  :title="log.error"
                  type="error"
                  show-icon
                  class="mt-4"
                />
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";

// 响应式状态
const activeTab = ref("generate");
const loading = ref(false);
const error = ref(null);
const generatedImage = ref(null);
const logs = ref([]);
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const formRef = ref(null);

// 表单数据
const formData = reactive({
  model: "cogview-3-flash",
  prompt: "",
  size: "1024x1024",
});

// 表单验证规则
const rules = {
  model: [{ required: true, message: "请选择模型", trigger: "change" }],
  prompt: [{ required: true, message: "请输入提示词", trigger: "blur" }],
  size: [{ required: true, message: "请选择尺寸", trigger: "change" }],
};

// 选项数据
const modelOptions = [
  { value: "cogview-3", label: "CogView-3(暂时不支持)" },
  { value: "cogview-3-plus", label: "CogView-3 Plus(暂时不支持)" },
  { value: "cogview-3-flash", label: "CogView-3 Flash" },
];

const sizeOptions = [
  { value: "1024x1024", label: "方形 (1024x1024)" },
  { value: "768x1344", label: "竖版 (768x1344)" },
  { value: "864x1152", label: "竖版 (864x1152)" },
  { value: "1344x768", label: "横版 (1344x768)" },
  { value: "1152x864", label: "横版 (1152x864)" },
  { value: "1440x720", label: "横版 (1440x720)" },
  { value: "720x1440", label: "竖版 (720x1440)" },
];

// 生成图片
const generateImage = async () => {
  try {
    await formRef.value?.validate();

    loading.value = true;
    error.value = null;

    const data = await request("/api/cogview/generations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    generatedImage.value = data.data[0].url;
    ElMessage.success({
      message: "图片生成成功",
      plain: true,
    });
    fetchLogs(); // 刷新历史记录
  } catch (err) {
    error.value = err.response ? await err.response.text() : err.message;
    ElMessage.error({
      message: error.value,
      plain: true,
    });
  } finally {
    loading.value = false;
  }
};

// 添加下载图片方法
const downloadImage = async () => {
  try {
    if (!generatedImage.value) return;

    // 创建一个链接
    const link = document.createElement("a");

    // 获取图片文件名（从URL中提取或使用默认名称）
    const fileName =
      generatedImage.value.split("/").pop() || "generated-image.png";

    try {
      // 尝试使用fetch下载图片
      const response = await fetch(generatedImage.value);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      ElMessage.success({
        message: "图片下载成功",
        plain: true,
      });
    } catch (error) {
      // 如果fetch失败，回退到直接打开图片链接
      link.href = generatedImage.value;
      link.download = fileName;
      link.target = "_blank";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  } catch (err) {
    console.error("下载失败:", err);
    ElMessage.error({
      message: "下载失败，请稍后重试",
      plain: true,
    });
  }
};

// 获取历史记录
const fetchLogs = async () => {
  try {
    const data = await request(
      `/api/cogview/logs?skip=${
        (currentPage.value - 1) * pageSize.value
      }&limit=${pageSize.value}`
    );
    logs.value = data.items;
    total.value = data.total;
  } catch (err) {
    console.error("获取历史记录失败:", err);
    ElMessage.error({
      message: "获取历史记录失败",
      plain: true,
    });
  }
};

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val;
  fetchLogs();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchLogs();
};

// 日期格式化
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString();
};

// 组件挂载时获取历史记录
onMounted(() => {
  fetchLogs();
});
</script>

<style scoped>
.image-generator {
  min-height: 100vh;
  background-color: #f5f5f5;
}
:deep(.el-tabs__nav) {
  padding: 1rem 2rem 0;
}

:deep(.el-tabs__item) {
  font-size: 1rem;
  height: 3rem;
  line-height: 3rem;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #374151;
  padding-bottom: 0.5rem;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  background-color: rgb(249, 250, 251);
  border-color: rgb(229, 231, 235);
}

:deep(.el-button--primary) {
  background-color: #2563eb;
  border-color: #2563eb;
}

:deep(.el-button--primary:hover) {
  background-color: #1d4ed8;
  border-color: #1d4ed8;
}

:deep(.el-progress-bar__outer) {
  border-radius: 9999px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 9999px;
  transition: all 0.3s ease;
}
</style>
