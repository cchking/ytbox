<template>
  <div class="channel-management">
    <!-- 顶部操作区域 -->
    <div class="mb-4 md:mb-6 space-y-4">
      <div
        class="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
      >
        <div>
          <h2 class="text-xl md:text-2xl font-bold text-gray-900">渠道管理</h2>
          <p class="mt-1 text-sm text-gray-500">管理所有API渠道及其配置</p>
        </div>
        <el-button
          type="primary"
          @click="showChannelDialog = true"
          class="w-full md:w-auto bg-blue-600"
        >
          <plus class="w-4 h-4 mr-2" />添加渠道
        </el-button>
      </div>

      <div
        class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200"
      >
        <search class="w-5 h-5 mx-3 text-gray-400" />
        <el-input
          v-model="searchQuery"
          placeholder="搜索渠道名称、模型或代理地址..."
          class="flex-1 !border-none !shadow-none"
          clearable
          @input="handleSearch"
          @clear="clearSearch"
        />
      </div>
    </div>

    <!-- 渠道统计卡片 - 移动端改为单列布局 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <el-card shadow="hover" class="h-full">
        <div class="flex items-center">
          <div
            class="flex-shrink-0 w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center"
          >
            <database class="w-6 h-6 text-blue-500" />
          </div>
          <div class="ml-4">
            <div class="text-sm text-gray-500">活跃渠道</div>
            <div class="mt-1 text-2xl font-semibold">
              {{ statistics.activeChannels }}
              <span class="text-sm text-gray-500"
                >/ {{ statistics.totalChannels }}</span
              >
            </div>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="h-full">
        <div class="flex items-center">
          <div
            class="flex-shrink-0 w-12 h-12 rounded-full bg-green-50 flex items-center justify-center"
          >
            <layers class="w-6 h-6 text-green-500" />
          </div>
          <div class="ml-4">
            <div class="text-sm text-gray-500">总模型支持数</div>
            <div class="mt-1 text-2xl font-semibold">
              {{ statistics.uniqueModels.total }}
            </div>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="h-full">
        <div class="flex items-center mb-2">
          <div
            class="flex-shrink-0 w-12 h-12 rounded-full bg-purple-50 flex items-center justify-center"
          >
            <activity class="w-6 h-6 text-purple-500" />
          </div>
          <div class="ml-4">
            <div class="text-sm text-gray-500">权重分配</div>
          </div>
        </div>
        <div class="mt-2 h-2.5 bg-gray-100 rounded-full overflow-hidden">
          <div class="flex h-full">
            <div
              v-for="item in statistics.weightDistribution"
              :key="item.channelId"
              :style="{ width: `${item.percentage}%` }"
              class="h-full transition-all duration-300 ease-in-out bg-blue-500"
              :title="`${item.percentage}%`"
            ></div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 渠道列表 - 响应式布局 -->
    <div class="space-y-4">
      <!-- 电脑端表格视图 -->
      <div class="hidden md:block">
        <el-card>
          <el-table :data="channels" stripe style="width: 100%">
            <el-table-column label="渠道信息" min-width="200">
              <template #default="{ row }">
                <div class="flex items-center">
                  <div
                    class="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-medium"
                  >
                    {{ row.channel_name.charAt(0) }}
                  </div>
                  <div class="ml-4">
                    <div class="font-medium text-gray-900">
                      {{ row.channel_name }}
                    </div>
                    <div class="text-sm text-gray-500 mt-0.5">
                      <span class="inline-flex items-center">
                        <link-2 class="w-4 h-4 mr-1" />{{ row.base_url }}
                      </span>
                    </div>
                    <div class="text-sm text-gray-400 mt-0.5">
                      ID: {{ row.id }}
                    </div>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="模型配置" min-width="200">
              <template #default="{ row }">
                <div>
                  <div class="font-medium">
                    默认模型: {{ row.channel_model_name }}
                  </div>
                  <div class="mt-2 flex flex-wrap gap-1">
                    <el-tag
                      v-for="model in row.models"
                      :key="model"
                      size="small"
                      class="mr-1 mb-1"
                    >
                      {{ model }}
                    </el-tag>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="权重与状态" width="160">
              <template #default="{ row }">
                <div class="flex items-center gap-2">
                  <el-input-number
                    v-model="row.weight"
                    :min="0"
                    :max="100"
                    :step="0.1"
                    size="small"
                    @change="updateWeight(row)"
                    style="width: 90px"
                  />
                  <el-tag
                    :type="row.is_active ? 'success' : 'danger'"
                    size="small"
                  >
                    {{ row.is_active ? "启用" : "禁用" }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="320" fixed="right">
              <template #default="{ row }">
                <div class="flex items-center flex-nowrap gap-1">
                  <el-dropdown
                    trigger="click"
                    @command="(command) => handleTestCommand(command, row)"
                  >
                    <el-button type="primary" size="small">
                      <brain-circuit class="w-4 h-4" />
                      <span class="ml-1">测试</span>
                      <template v-if="getTestingCount(row.id) > 0">
                        <span class="mx-1">•</span>
                        <span>{{ getTestingCount(row.id) }}</span>
                      </template>
                      <chevron-down class="w-4 h-4 ml-1" />
                    </el-button>

                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item :command="{ type: 'default' }">
                          默认模型 ({{ row.channel_model_name }})
                        </el-dropdown-item>
                        <el-dropdown-item :command="{ type: 'all' }">
                          测试所有模型
                        </el-dropdown-item>
                        <el-dropdown-item divided />
                        <el-dropdown-item
                          v-for="model in row.models"
                          :key="model"
                          :command="{ type: 'model', model }"
                        >
                          {{ model }}
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>

                  <el-button
                    type="primary"
                    size="small"
                    @click="editChannel(row)"
                  >
                    <edit class="w-4 h-4" />
                    编辑
                  </el-button>

                  <el-button
                    :type="row.is_active ? 'danger' : 'success'"
                    size="small"
                    @click="toggleChannel(row)"
                  >
                    <power class="w-4 h-4" />
                    {{ row.is_active ? "禁用" : "启用" }}
                  </el-button>

                  <el-button
                    type="danger"
                    size="small"
                    @click="handleDelete(row)"
                  >
                    <trash2 class="w-4 h-4" />
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 移动端卡片式布局 -->
      <div class="md:hidden space-y-4">
        <el-card v-for="row in channels" :key="row.id" class="channel-card">
          <!-- 渠道头部信息 -->
          <div class="flex items-start gap-3 mb-4">
            <div
              class="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-medium"
            >
              {{ row.channel_name.charAt(0) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-900">
                {{ row.channel_name }}
              </div>
              <div class="text-sm text-gray-500 mt-0.5 flex items-center">
                <link-2 class="w-4 h-4 mr-1 flex-shrink-0" />
                <span class="truncate">{{ row.base_url }}</span>
              </div>
              <div class="text-sm text-gray-400 mt-0.5">ID: {{ row.id }}</div>
            </div>
          </div>

          <!-- 模型信息 -->
          <div class="mb-4">
            <div class="font-medium mb-2">
              默认模型: {{ row.channel_model_name }}
            </div>
            <div class="flex flex-wrap gap-1">
              <el-tag
                v-for="model in row.models"
                :key="model"
                size="small"
                class="mb-1"
              >
                {{ model }}
              </el-tag>
            </div>
          </div>

          <!-- 权重与状态 -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <el-input-number
                v-model="row.weight"
                :min="0"
                :max="100"
                :step="0.1"
                size="small"
                @change="updateWeight(row)"
                class="!w-24"
              />
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                {{ row.is_active ? "启用" : "禁用" }}
              </el-tag>
            </div>
          </div>

          <!-- 操作按钮 - 移动端网格布局 -->
          <div class="grid grid-cols-2 gap-2">
            <el-dropdown
              trigger="click"
              @command="(command) => handleTestCommand(command, row)"
              class="w-full"
            >
              <el-button type="primary" size="small" class="w-full">
                <brain-circuit class="w-4 h-4" />
                <span class="ml-1">测试</span>
                <template v-if="getTestingCount(row.id) > 0">
                  <span class="mx-1">•</span>
                  <span>{{ getTestingCount(row.id) }}</span>
                </template>
                <chevron-down class="w-4 h-4 ml-1" />
              </el-button>

              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="{ type: 'default' }">
                    默认模型 ({{ row.channel_model_name }})
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ type: 'all' }">
                    测试所有模型
                  </el-dropdown-item>
                  <el-dropdown-item divided />
                  <el-dropdown-item
                    v-for="model in row.models"
                    :key="model"
                    :command="{ type: 'model', model }"
                  >
                    {{ model }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <el-button
              type="primary"
              size="small"
              @click="editChannel(row)"
              class="w-full"
            >
              <edit class="w-4 h-4" />
              编辑
            </el-button>

            <el-button
              :type="row.is_active ? 'danger' : 'success'"
              size="small"
              @click="toggleChannel(row)"
              class="w-full"
            >
              <power class="w-4 h-4" />
              {{ row.is_active ? "禁用" : "启用" }}
            </el-button>

            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              class="w-full"
            >
              <trash2 class="w-4 h-4" />
              删除
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 添加/编辑渠道对话框 -->
    <div v-if="showChannelDialog" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="fixed inset-0 bg-black bg-opacity-50"></div>
      <div class="min-h-screen px-4 text-center">
        <span class="inline-block h-screen align-middle">&#8203;</span>

        <div
          class="inline-block w-full max-w-md md:max-w-2xl p-4 md:p-6 my-8 text-left align-middle bg-white rounded-lg shadow transform relative"
        >
          <!-- 对话框标题 -->
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold">
              {{ selectedChannel ? "编辑渠道" : "创建新的渠道" }}
            </h2>
            <button
              @click="closeChannelDialog"
              class="text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <x class="w-6 h-6" />
            </button>
          </div>

          <!-- 渠道表单 -->
          <form @submit.prevent="handleSubmit" class="space-y-4 md:space-y-6">
            <!-- 类型选择 -->
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >类型</label
              >
              <select
                v-model="formData.type"
                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="OpenAI">OpenAI</option>
              </select>
            </div>

            <!-- 名称 -->
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >名称</label
              >
              <input
                type="text"
                v-model="formData.channel_name"
                placeholder="请为渠道命名"
                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:ring-blue-500"
                required
              />
            </div>

            <!-- 代理设置 -->
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >代理</label
              >
              <input
                type="text"
                v-model="formData.proxy"
                placeholder="请输入API代理地址"
                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500"
                required
              />
            </div>

            <!-- 已添加的模型列表 -->
            <div v-if="formData.models.length > 0" class="mt-2">
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="model in formData.models"
                  :key="model"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-md bg-blue-50 text-sm text-blue-700 border border-blue-200"
                >
                  {{ model }}
                  <button
                    type="button"
                    @click="removeModel(model)"
                    class="ml-1.5 text-blue-600 hover:text-blue-800"
                  >
                    <x class="w-3.5 h-3.5" />
                  </button>
                </span>
              </div>
            </div>

            <!-- 添加模型 -->
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >添加模型</label
              >
              <div class="mt-1 flex items-stretch">
                <input
                  type="text"
                  v-model="modelInput"
                  placeholder="输入自定义模型名称"
                  class="flex-grow rounded-l-md border border-r-0 border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500"
                  @keyup.enter="handleAddModels"
                />
                <button
                  type="button"
                  @click="handleAddModels"
                  class="px-3 text-sm bg-blue-50 text-blue-600 border border-l-0 border-gray-300 rounded-r-md hover:bg-blue-100 transition-colors duration-200"
                >
                  插入
                </button>
              </div>

              <!-- 快捷操作按钮 -->
              <div class="mt-2 space-x-2">
                <button
                  type="button"
                  @click="addAllModels"
                  class="text-sm text-blue-600 hover:text-blue-800 transition-colors duration-200"
                >
                  添加常用模型
                </button>
                <button
                  type="button"
                  @click="clearModels"
                  class="text-sm text-red-600 hover:text-red-800 transition-colors duration-200"
                >
                  清空列表
                </button>
              </div>
            </div>

            <!-- 模型重定向 -->
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >模型重定向</label
              >
              <textarea
                v-model="formData.modelMapping"
                rows="4"
                placeholder='此项可选，用于修改请求中的模型名称，为一个 JSON 字符串，键为请求中的模型名称，值为变更后的模型名称，例如:&#13;&#10;{&#13;&#10;  "gpt-3.5-turbo": "gpt-3.5-turbo-0125"&#13;&#10;}'
                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500"
              ></textarea>
            </div>

            <!-- API Key -->
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >密钥</label
              >
              <input
                type="password"
                v-model="formData.api_key"
                :placeholder="
                  selectedChannel ? '不修改请留空' : '请输入通道对应的密钥'
                "
                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:ring-blue-500"
                :required="!selectedChannel"
              />
            </div>

            <!-- 组织 -->
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >组织</label
              >
              <input
                type="text"
                v-model="formData.organization"
                placeholder="请输入组织ID org-xxx"
                class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <!-- 权重 -->
            <div>
              <label class="block text-sm font-medium text-gray-700"
                >权重</label
              >
              <input
                type="number"
                v-model.number="formData.weight"
                class="mt-1 block w-32 rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
                min="0"
                max="100"
                step="0.1"
                required
              />
            </div>

            <!-- 启用状态 -->
            <div class="flex items-center">
              <input
                type="checkbox"
                v-model="formData.is_active"
                id="is_active"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label for="is_active" class="ml-2 text-sm text-gray-700"
                >启用此渠道</label
              >
            </div>

            <!-- 错误信息 -->
            <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>

            <!-- 按钮组 -->
            <div class="flex justify-end space-x-3 mt-6">
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {{
                  isSubmitting ? "提交中..." : selectedChannel ? "保存" : "添加"
                }}
              </button>
              <button
                type="button"
                @click="closeChannelDialog"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 确认删除对话框 -->
    <el-dialog
      v-model="showConfirmDialog"
      title="确认删除"
      :width="isMobile ? '90%' : '30%'"
      class="responsive-dialog"
    >
      <el-result
        icon="warning"
        title="确认删除渠道?"
        :sub-title="`确定要删除渠道 '${confirmData?.channel_name}' 吗？此操作无法撤销。`"
      >
        <template #extra>
          <div class="flex justify-end space-x-3">
            <el-button @click="closeConfirmDialog">取消</el-button>
            <el-button
              type="danger"
              @click="handleConfirm"
              :loading="isDeleting"
            >
              {{ isDeleting ? "删除中..." : "确认删除" }}
            </el-button>
          </div>
        </template>
      </el-result>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import {
  Plus,
  Search,
  ChevronDown,
  Edit,
  Trash2,
  Power,
  BrainCircuit,
  Database,
  Layers,
  Activity,
  Link2,
  X,
} from "lucide-vue-next";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";

// 响应式变量
const channels = ref([]);
const models = ref([]);
const showChannelDialog = ref(false);
const selectedChannel = ref(null);
const error = ref("");
const isSubmitting = ref(false);
const modelInput = ref("");
const searchQuery = ref("");
const testingModels = ref(new Map()); // Map<channelId_modelName, boolean>
const showConfirmDialog = ref(false);
const confirmData = ref(null);
const isDeleting = ref(false);
let searchDebounce = null;

// 表单数据
const formData = ref({
  type: "OpenAI",
  channel_name: "",
  api_key: "",
  weight: 1.0,
  is_active: true,
  proxy: "",
  organization: "",
  models: [],
  modelMapping: "",
  target_model_id: null,
});

// 添加统计数据的响应式变量
const statistics = ref({
  activeChannels: 0,
  totalChannels: 0,
  uniqueModels: {
    total: 0,
    models: [],
  },
  weightDistribution: [],
});

// 获取统计数据的函数
const fetchChannelStats = async () => {
  try {
    const response = await request("/api/admin/channels/stats");
    statistics.value = response;
  } catch (err) {
    console.error("Failed to fetch channel stats:", err);
    ElMessage.error({
      message: "获取渠道统计失败: " + err.message,
      plain: true,
    });
  }
};
// 计算总模型数量
const getTotalModels = () => {
  return channels.value.reduce((total, channel) => {
    return total + (Array.isArray(channel.models) ? channel.models.length : 0);
  }, 0);
};

// 获取某个渠道正在测试的模型数量
const getTestingCount = (channelId) => {
  return Array.from(testingModels.value.keys()).filter((key) =>
    key.startsWith(`${channelId}_`)
  ).length;
};

// 处理搜索
const handleSearch = () => {
  if (searchDebounce) clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    fetchChannels();
  }, 300);
};

// 清除搜索
const clearSearch = () => {
  searchQuery.value = "";
  fetchChannels();
};

// 测试渠道
const testChannel = async (channel, modelName = null) => {
  const testKey = `${channel.id}_${modelName || "default"}`;
  if (testingModels.value.get(testKey)) return;

  try {
    testingModels.value.set(testKey, true);

    const url = `/api/admin/channels/${
      channel.id
    }/test?model_name=${encodeURIComponent(
      modelName || channel.channel_model_name
    )}`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        `渠道${channel.id} 状态码:${response.status} 响应:${
          data.detail || response.statusText
        }`
      );
    }

    // 成功响应显示测试的模型名称和延迟
    ElMessage({
      type: "success",
      message: `渠道${channel.id} 模型:${data.model_tested} 延迟:${data.latency}ms`,
      plain: true,
    });
  } catch (err) {
    ElMessage({
      type: "error",
      message: err.message,
      plain: true,
    });
  } finally {
    testingModels.value.delete(testKey);
  }
};
// 测试所有模型
const testAllModels = async (channel) => {
  const testPromises = [
    testChannel(channel), // 测试默认模型
    ...channel.models
      .filter((model) => model !== channel.channel_model_name) // 跳过默认模型
      .map((model) => testChannel(channel, model)),
  ];

  // 并行执行所有测试
  await Promise.all(testPromises);
};

// 处理测试命令
const handleTestCommand = (command, channel) => {
  if (command.type === "default") {
    testChannel(channel);
  } else if (command.type === "model") {
    testChannel(channel, command.model);
  } else if (command.type === "all") {
    testAllModels(channel);
  }
};

// 添加模型
const handleAddModels = () => {
  if (!modelInput.value.trim()) return;

  const newModels = modelInput.value
    .split(";")
    .map((model) => model.trim())
    .filter((model) => model && !formData.value.models.includes(model));

  if (newModels.length > 0) {
    formData.value.models = [...formData.value.models, ...newModels];
  }
  modelInput.value = "";
};

// 移除单个模型
const removeModel = (model) => {
  formData.value.models = formData.value.models.filter((m) => m !== model);
};

// 清除所有模型
const clearModels = () => {
  formData.value.models = [];
};

// 快速添加所有 GPT-3.5 模型
const addAllModels = () => {
  formData.value.models = [
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-16k-0613",
  ];
};

// 计算权重百分比
const getWeightPercentage = (channel) => {
  const totalWeight = channels.value.reduce(
    (sum, c) => sum + (c.is_active ? c.weight : 0),
    0
  );
  return totalWeight === 0
    ? 0
    : ((channel.weight / totalWeight) * 100).toFixed(1);
};

// 更新权重
const updateWeight = async (channel) => {
  try {
    const updateData = {
      channel_name: channel.channel_name,
      channel_model_name: channel.channel_model_name,
      base_url: channel.base_url,
      weight: Number(channel.weight),
      is_active: channel.is_active,
      organization: channel.organization || "",
      models: channel.models,
      redirect_mapping: channel.redirect_mapping,
    };

    await request(`/api/admin/channels/${channel.id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updateData), // 使用 JSON.stringify() 序列化数据
    });

    await fetchChannels();
    ElMessage.success({
      message: "权重更新成功",
      plain: true,
    });
  } catch (err) {
    console.error("Failed to update weight:", err);
    ElMessage.error({
      message: "权重更新失败: " + err.message,
      plain: true,
    });
  }
};

// 编辑渠道
const editChannel = (channel) => {
  selectedChannel.value = channel;
  formData.value = {
    type: "OpenAI",
    channel_name: channel.channel_name,
    channel_model_name: channel.channel_model_name,
    proxy: channel.base_url,
    api_key: "",
    weight: channel.weight,
    is_active: channel.is_active,
    organization: channel.organization || "",
    models: channel.models || [],
    modelMapping: channel.redirect_mapping || "",
  };
  showChannelDialog.value = true;
};

// 切换渠道状态
const toggleChannel = async (channel) => {
  try {
    await request(`/api/admin/channels/${channel.id}/toggle`, {
      method: "PATCH",
    });
    await fetchChannels();
    ElMessage.success({
      message: `渠道已${channel.is_active ? "禁用" : "启用"}`,
      plain: true,
    });
  } catch (err) {
    error.value = err.message;
    ElMessage.error({
      message: "状态切换失败: " + err.message,
      plain: true,
    });
  }
};

// 删除渠道
const handleDelete = async (channel) => {
  if (!confirm(`确定要删除渠道 "${channel.channel_name}" 吗？`)) return;

  try {
    await request(`/api/admin/channels/${channel.id}`, {
      method: "DELETE", // 使用 DELETE 方法
      headers: {
        "Content-Type": "application/json",
      },
    });
    await fetchChannels();
    ElMessage.success({
      message: "渠道删除成功",
      plain: true,
    });
  } catch (error) {
    console.error("Failed to delete channel:", error);
    ElMessage.error({
      message: "删除失败: " + error.message,
      plain: true,
    });
  }
};

// 确认删除
const handleConfirm = async () => {
  if (!confirmData.value) return;

  try {
    isDeleting.value = true;
    await request(`/api/admin/channels/${confirmData.value.id}`, {
      method: "DELETE",
    });
    await fetchChannels();
    ElMessage.success({
      message: "渠道删除成功",
      plain: true,
    });
    closeConfirmDialog();
  } catch (err) {
    error.value = err.message;
    ElMessage.error({
      message: "删除失败: " + err.message,
      plain: true,
    });
  } finally {
    isDeleting.value = false;
  }
};

// 关闭确认对话框
const closeConfirmDialog = () => {
  showConfirmDialog.value = false;
  confirmData.value = null;
};

// 关闭渠道对话框
const closeChannelDialog = () => {
  showChannelDialog.value = false;
  selectedChannel.value = null;
  modelInput.value = "";
  formData.value = {
    type: "OpenAI",
    channel_name: "",
    api_key: "",
    weight: 1.0,
    is_active: true,
    proxy: "",
    organization: "",
    models: [],
    modelMapping: "",
  };
  error.value = "";
};

// 获取渠道列表
const fetchChannels = async () => {
  try {
    const url = searchQuery.value
      ? `/api/admin/channels/search?query=${encodeURIComponent(
          searchQuery.value
        )}`
      : "/api/admin/channels";

    const res = await request(url);
    channels.value = res;
  } catch (err) {
    console.error("Failed to fetch channels:", err);
    error.value = err.message;
    ElMessage.error({
      message: "获取渠道列表失败: " + err.message,
      plain: true,
    });
  }
};

// 获取模型列表
const fetchModels = async () => {
  try {
    const res = await request("/api/models");
    models.value = res;
  } catch (err) {
    console.error("Failed to fetch models:", err);
    error.value = err.message;
    ElMessage.error({
      message: "获取模型列表失败: " + err.message,
      plain: true,
    });
  }
};

// 处理表单提交
const handleSubmit = async () => {
  error.value = "";
  isSubmitting.value = true;
  try {
    // 验证必填字段
    if (
      !formData.value.channel_name ||
      !formData.value.proxy ||
      formData.value.models.length === 0
    ) {
      throw new Error("请填写所有必填字段");
    }

    // 确保 proxy 包含协议
    let baseUrl = formData.value.proxy;
    if (!baseUrl.startsWith("http://") && !baseUrl.startsWith("https://")) {
      baseUrl = "https://" + baseUrl;
    }

    // 构造提交数据
    const submitData = {
      type: formData.value.type,
      channel_name: formData.value.channel_name,
      channel_model_name: formData.value.models[0] || "",
      base_url: baseUrl, // 使用处理后的 URL
      api_key: formData.value.api_key,
      weight: Number(formData.value.weight),
      is_active: Boolean(formData.value.is_active),
      organization: formData.value.organization || "",
      models: formData.value.models,
      redirect_mapping: formData.value.modelMapping || null,
    };

    console.log("Submitting data:", submitData);

    const method = selectedChannel.value ? "PUT" : "POST";
    const url = selectedChannel.value
      ? `/api/admin/channels/${selectedChannel.value.id}`
      : "/api/admin/channels";

    console.log("Request URL:", url);
    console.log("Request Method:", method);

    const response = await request(url, {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(submitData),
    });

    await fetchChannels();
    ElMessage.success({
      message: `渠道${selectedChannel.value ? "更新" : "创建"}成功`,
      plain: true,
    });
    closeChannelDialog();
  } catch (err) {
    console.error("Submit error:", err);
    error.value = err.message;
    ElMessage.error({
      message: `${selectedChannel.value ? "更新" : "创建"}失败: ` + err.message,
      plain: true,
    });
  } finally {
    isSubmitting.value = false;
  }
};

// 在组件挂载时获取数据
onMounted(() => {
  fetchChannels();
  fetchChannelStats();
});
</script>

<style scoped>
.channel-management {
  padding: 20px;
}

.el-dropdown {
  vertical-align: top;
}

.el-button + .el-button {
  margin-left: 0;
}

/* 统一图标样式 */
:deep(.lucide) {
  display: inline-block;
  vertical-align: middle;
}

:deep(.el-button) {
  padding: 5px 10px;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}

:deep(.el-button .lucide) {
  margin-right: 2px;
  width: 14px;
  height: 14px;
}

:deep(.el-input-number) {
  width: 90px !important;
}
</style>
