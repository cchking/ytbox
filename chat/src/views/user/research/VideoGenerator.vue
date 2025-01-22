<!-- VideoGenerator.vue -->
<template>
  <div class="min-h-screen bg-gray-50/50 pb-8">
    <div class="max-w-5xl mx-auto px-4 pt-6">
      <!-- 标签页 -->
      <el-tabs
        v-model="activeTab"
        class="bg-white rounded-xl shadow-sm border border-gray-100"
      >
        <!-- 生成视频标签页 -->
        <el-tab-pane label="生成视频" name="generate">
          <div class="px-8 py-6">
            <div class="flex items-center gap-3 mb-8">
              <div class="w-1 h-8 bg-blue-500 rounded-full"></div>
              <h2 class="text-2xl font-bold text-gray-800">AI 视频生成</h2>
            </div>

            <!-- 主要内容分为左右两栏 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <!-- 左侧表单 -->
              <div>
                <el-form
                  :model="formData"
                  :rules="rules"
                  ref="formRef"
                  label-position="top"
                  @submit.prevent="generateVideo"
                  class="space-y-6"
                >
                  <!-- 模型和生成模式分为两列 -->
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

                    <el-form-item label="生成模式" class="mb-0">
                      <el-radio-group
                        v-model="generationMode"
                        class="w-full flex bg-gray-50 p-1 rounded-lg"
                      >
                        <el-radio-button label="text" class="flex-1 !border-0"
                          >文本生成</el-radio-button
                        >
                        <el-radio-button label="image" class="flex-1 !border-0"
                          >图片生成</el-radio-button
                        >
                      </el-radio-group>
                    </el-form-item>
                  </div>

                  <!-- 提示词输入框 -->
                  <el-form-item label="提示词描述" prop="prompt" class="mb-0">
                    <el-input
                      v-model="formData.prompt"
                      type="textarea"
                      :rows="4"
                      placeholder="请详细描述您想要生成的视频内容..."
                      resize="none"
                      class="!bg-gray-50"
                    />
                  </el-form-item>

                  <!-- 图片上传区域 -->
                  <el-form-item
                    v-if="generationMode === 'image'"
                    label="上传参考图片"
                    prop="image_url"
                    class="mb-0"
                  >
                    <div
                      class="w-full aspect-video bg-gray-50 rounded-lg border-2 border-dashed border-gray-200 hover:border-blue-400 transition-colors cursor-pointer relative flex items-center justify-center"
                      @click="triggerFileInput"
                      v-if="!uploadedImage.url"
                    >
                      <input
                        type="file"
                        ref="fileInput"
                        @change="handleFileChange"
                        accept="image/jpeg,image/png"
                        class="hidden"
                      />
                      <div class="text-center">
                        <div class="text-gray-400 mb-2">
                          <i class="el-icon-upload text-3xl"></i>
                        </div>
                        <p class="text-sm text-gray-600">
                          点击或拖拽图片到此处上传
                        </p>
                        <p class="text-xs text-gray-400 mt-1">
                          支持 JPG/PNG 格式，最大 5MB
                        </p>
                      </div>
                      <el-button
                        v-if="uploading"
                        :loading="true"
                        class="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center"
                      >
                        上传中...
                      </el-button>
                    </div>

                    <!-- 已上传图片预览 -->
                    <div
                      v-else
                      class="relative group"
                      @click="triggerFileInput"
                    >
                      <img
                        :src="uploadedImage.url"
                        class="w-full aspect-video object-cover rounded-lg"
                      />
                      <div
                        class="absolute inset-0 bg-black bg-opacity-40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                      >
                        <el-button type="primary">更换图片</el-button>
                      </div>
                    </div>
                  </el-form-item>

                  <!-- 视频参数设置分组 -->
                  <div
                    class="bg-gray-50/50 rounded-xl p-6 space-y-6 border border-gray-100"
                  >
                    <h3 class="font-medium text-gray-700">视频参数设置</h3>

                    <!-- 尺寸和质量选择 -->
                    <div class="grid grid-cols-2 gap-4">
                      <el-form-item label="视频尺寸" prop="size" class="mb-0">
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

                      <el-form-item
                        v-if="formData.model !== 'cogvideox-flash'"
                        label="输出质量"
                        prop="quality"
                        class="mb-0"
                      >
                        <el-select
                          v-model="formData.quality"
                          placeholder="请选择质量"
                          class="w-full"
                        >
                          <el-option label="质量优先" value="quality" />
                          <el-option label="速度优先" value="speed" />
                        </el-select>
                      </el-form-item>
                    </div>

                    <!-- 时长和帧率选择 -->
                    <div
                      v-if="generationMode === 'image'"
                      class="grid grid-cols-2 gap-4"
                    >
                      <el-form-item
                        label="视频时长"
                        prop="duration"
                        class="mb-0"
                      >
                        <el-select
                          v-model="formData.duration"
                          placeholder="选择时长"
                          class="w-full"
                        >
                          <el-option label="5秒" :value="5" />
                          <el-option label="10秒" :value="10" />
                        </el-select>
                      </el-form-item>

                      <el-form-item label="视频帧率" prop="fps" class="mb-0">
                        <el-select
                          v-model="formData.fps"
                          placeholder="选择帧率"
                          class="w-full"
                        >
                          <el-option label="30fps" :value="30" />
                          <el-option label="60fps" :value="60" />
                        </el-select>
                      </el-form-item>
                    </div>

                    <!-- AI音效开关 -->
                    <el-form-item label="AI音效" class="!mb-0">
                      <el-switch v-model="formData.with_audio" />
                    </el-form-item>
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
                    @click="generateVideo"
                    :disabled="isGenerateDisabled"
                  >
                    {{ loading ? "视频生成中..." : "开始生成" }}
                  </el-button>
                </el-form>
              </div>

              <!-- 右侧预览区域 -->
              <div class="space-y-6">
                <!-- 生成状态和进度 -->
                <div v-if="currentTaskId" class="bg-blue-50 rounded-lg p-6">
                  <div class="flex items-center gap-3 mb-4">
                    <el-icon class="text-blue-500"><Loading /></el-icon>
                    <span class="font-medium text-blue-700">{{
                      getTaskStatusText()
                    }}</span>
                  </div>
                  <el-progress
                    :percentage="taskProgress"
                    :status="taskStatus === 'FAIL' ? 'exception' : undefined"
                    :stroke-width="10"
                  />
                </div>

                <!-- 生成结果展示 -->
                <div
                  v-if="generatedVideo"
                  class="bg-white rounded-lg shadow-sm p-4 border border-gray-100"
                >
                  <h3 class="font-medium text-gray-700 mb-4">生成结果</h3>
                  <video
                    :src="generatedVideo"
                    :poster="generatedVideoCover"
                    controls
                    class="w-full aspect-video rounded-lg bg-gray-100"
                  >
                    您的浏览器不支持视频播放
                  </video>
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

            <!-- 历史记录列表 -->
            <div class="space-y-6">
              <el-empty v-if="logs.length === 0" description="暂无生成记录" />

              <div
                v-for="log in logs"
                :key="log.id"
                class="bg-white rounded-lg shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow"
              >
                <!-- 记录头部信息 -->
                <div class="grid grid-cols-2 gap-4 mb-4">
                  <div class="space-y-1">
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
                  <div class="text-right">
                    <span class="text-sm text-gray-500">
                      {{ formatDate(log.created_at) }}
                    </span>
                  </div>
                </div>

                <!-- 提示词 -->
                <p
                  v-if="log.prompt"
                  class="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 mb-4"
                >
                  {{ log.prompt }}
                </p>

                <div class="grid grid-cols-2 gap-6">
                  <!-- 左侧参考图 -->
                  <div v-if="log.image_url">
                    <p class="text-sm font-medium text-gray-600 mb-2">
                      参考图片:
                    </p>
                    <img
                      :src="log.image_url"
                      class="w-full aspect-video object-cover rounded-lg"
                      alt="参考图片"
                    />
                  </div>

                  <!-- 右侧视频结果 -->
                  <div class="relative">
                    <p class="text-sm font-medium text-gray-600 mb-2">
                      生成视频:
                    </p>
                    <video
                      v-if="log.video_url"
                      :src="log.video_url"
                      :poster="log.cover_image_url"
                      controls
                      class="w-full aspect-video rounded-lg bg-gray-100"
                    >
                      您的浏览器不支持视频播放
                    </video>

                    <!-- 生成中状态 -->
                    <div
                      v-if="log.status === 'PROCESSING'"
                      class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-lg mt-7"
                    >
                      <el-spinner class="text-white" />
                      <span class="text-white ml-2">生成中... </span>
                    </div>
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
import { ref, reactive, computed, onMounted, onUnmounted, watch } from "vue";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";

// 响应式状态
const activeTab = ref("generate");
const loading = ref(false);
const uploading = ref(false);
const error = ref(null);
const generationMode = ref("text");
const generatedVideo = ref(null);
const generatedVideoCover = ref(null);
const currentTaskId = ref(null);
const taskStatus = ref(null);
const taskProgress = ref(0);
const progressInterval = ref(null);
const logs = ref([]);
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const formRef = ref(null);
const fileInput = ref(null);

// 上传的图片信息
const uploadedImage = reactive({
  id: "",
  url: "",
});

// 表单数据
const formData = reactive({
  model: "cogvideox-flash",
  prompt: "",
  quality: "quality",
  with_audio: false,
  size: "1920x1080",
  duration: 5,
  fps: 30,
});

// 计算生成按钮是否禁用
const isGenerateDisabled = computed(() => {
  if (generationMode.value === "image") {
    return !uploadedImage.url;
  }
  return false;
});

// 表单验证规则
const rules = {
  model: [{ required: true, message: "请选择模型", trigger: "change" }],
  size: [{ required: true, message: "请选择尺寸", trigger: "change" }],
};

// 选项数据
const modelOptions = [
  { value: "cogvideox", label: "CogVideoX (暂时不支持)" },
  { value: "cogvideox-flash", label: "CogVideoX Flash (快速)" },
];

const sizeOptions = [
  { value: "720x480", label: "标清 (720x480)" },
  { value: "1024x1024", label: "方形 (1024x1024)" },
  { value: "1280x960", label: "高清 (1280x960)" },
  { value: "960x1280", label: "竖版高清 (960x1280)" },
  { value: "1920x1080", label: "全高清 (1920x1080)" },
  { value: "1080x1920", label: "竖版全高清 (1080x1920)" },
  { value: "2048x1080", label: "2K (2048x1080)" },
  { value: "3840x2160", label: "4K (3840x2160)" },
];

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click();
};

// 文件改变处理
const handleFileChange = async (event) => {
  if (!event.target.files || !event.target.files.length) return;

  const file = event.target.files[0];

  // 验证文件类型
  const isValidType = ["image/jpeg", "image/png"].includes(file.type);
  if (!isValidType) {
    ElMessage.error({
      message: "只能上传 JPG 或 PNG 格式的图片！",
      plain: true,
    });
    event.target.value = "";
    return;
  }

  // 验证文件大小
  const isLt5M = file.size / 1024 / 1024 < 5;
  if (!isLt5M) {
    ElMessage.error({
      message: "图片大小不能超过 5MB！",
      plain: true,
    });
    event.target.value = "";
    return;
  }

  uploading.value = true;
  error.value = null;

  try {
    const formData = new FormData();
    formData.append("files", file);

    // 上传文件
    const response = await request("/api/upload", {
      method: "POST",
      body: formData,
    });

    if (response.files && response.files.length > 0) {
      const fileInfo = response.files[0];
      uploadedImage.id = fileInfo.id;
      uploadedImage.url = fileInfo.url;
      ElMessage.success({
        message: "图片上传成功",
        plain: true,
      });
    } else {
      throw new Error("上传失败：未收到文件信息");
    }
  } catch (err) {
    ElMessage.error({
      message: `上传失败: ${err.message}`,
      plain: true,
    });
  } finally {
    uploading.value = false;
    event.target.value = "";
  }
};

// 生成视频
const generateVideo = async () => {
  try {
    await formRef.value?.validate();

    loading.value = true;
    error.value = null;
    currentTaskId.value = null;
    taskStatus.value = null;
    taskProgress.value = 0;

    // 构建请求数据
    const requestData = {
      model: formData.model,
      prompt: formData.prompt || undefined,
      quality: formData.quality,
      with_audio: formData.with_audio,
      size: formData.size,
      duration: formData.duration,
      fps: formData.fps,
    };

    // 如果是图片生成模式，添加图片信息
    if (generationMode.value === "image") {
      if (!uploadedImage.url) {
        throw new Error("请先上传图片");
      }
      requestData.image_url = uploadedImage.url;
      requestData.image_id = uploadedImage.id;
    }

    // 过滤掉未定义的值
    Object.keys(requestData).forEach(
      (key) => requestData[key] === undefined && delete requestData[key]
    );

    const data = await request("/api/cogvideo/generations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    currentTaskId.value = data.id;
    taskStatus.value = data.task_status;
    startProgressPolling();

    ElMessage.success({
      message: "视频生成任务已提交",
      plain: true,
    });
    await fetchLogs();
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

// 获取任务状态
const getTaskStatus = async () => {
  if (!currentTaskId.value) return;

  try {
    const response = await request(
      `/api/cogvideo/logs?task_id=${currentTaskId.value}`
    );
    const task = response.items[0];

    if (task) {
      taskStatus.value = task.status;
      if (task.status === "SUCCESS") {
        generatedVideo.value = task.video_url;
        generatedVideoCover.value = task.cover_image_url;
        stopProgressPolling();
        ElMessage.success({
          message: "视频生成成功",
          plain: true,
        });
      } else if (task.status === "FAIL") {
        error.value = task.error || "视频生成失败";
        stopProgressPolling();
        ElMessage.error({
          message: error.value,
          plain: true,
        });
      }
    }
  } catch (err) {
    console.error("获取任务状态失败:", err);
  }
};

// 开始轮询进度
const startProgressPolling = () => {
  progressInterval.value = setInterval(() => {
    if (taskProgress.value < 95) {
      taskProgress.value += 1;
    }
    getTaskStatus();
  }, 2000);
};

// 停止轮询进度
const stopProgressPolling = () => {
  if (progressInterval.value) {
    clearInterval(progressInterval.value);
    progressInterval.value = null;
  }
  if (taskStatus.value === "SUCCESS") {
    taskProgress.value = 100;
  }
};

// 获取任务状态文本
const getTaskStatusText = () => {
  switch (taskStatus.value) {
    case "PROCESSING":
      return "视频生成中，请耐心等待...";
    case "SUCCESS":
      return "视频生成完成！";
    case "FAIL":
      return "视频生成失败";
    default:
      return "";
  }
};

// 获取历史记录
const fetchLogs = async () => {
  try {
    const data = await request(
      `/api/cogvideo/logs?skip=${
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

// 监听生成模式变化
watch(generationMode, (newMode) => {
  error.value = null;

  // 重置图片信息
  if (newMode === "text") {
    uploadedImage.id = "";
    uploadedImage.url = "";
  }
});

// 组件挂载时获取历史记录
onMounted(() => {
  fetchLogs();
});

// 组件卸载时清理轮询定时器
onUnmounted(() => {
  stopProgressPolling();
});
</script>

<style scoped>
.video-generator {
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

:deep(.el-radio-button__inner) {
  padding: 0.5rem 1rem;
}

:deep(.el-progress-bar__outer) {
  border-radius: 9999px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 9999px;
  transition: all 0.3s ease;
}
</style>
