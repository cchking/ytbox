<template>
  <div class="p-6 space-y-8">
    <!-- 生成表单卡片 -->
    <div
      class="bg-white rounded-3xl shadow-lg p-6 transform transition-all duration-300 hover:shadow-xl"
      :class="{ 'opacity-75': generating }"
    >
      <div class="flex items-center mb-6">
        <div
          class="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center mr-4"
        >
          <Wand2 class="w-6 h-6 text-blue-500" />
        </div>
        <h2
          class="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
        >
          生成卡密
        </h2>
      </div>

      <!-- 表单内容 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- 类型选择 -->
        <div class="relative">
          <label class="text-sm text-gray-600 mb-2 block">卡密类型</label>
          <div
            class="relative group"
            :class="{ 'transform scale-105': form.type === 'vip' }"
          >
            <el-select v-model="form.type" class="w-full !rounded-lg">
              <el-option value="vip" label="VIP会员">
                <div class="flex items-center">
                  <Crown class="w-5 h-5 mr-2 text-yellow-500" />
                  <span>VIP会员</span>
                </div>
              </el-option>
              <el-option value="coin" label="金币">
                <div class="flex items-center">
                  <Coins class="w-5 h-5 mr-2 text-amber-500" />
                  <span>金币</span>
                </div>
              </el-option>
            </el-select>
          </div>
        </div>

        <!-- 面值输入 -->
        <div>
          <label class="text-sm text-gray-600 mb-2 block">
            {{ form.type === "vip" ? "VIP天数" : "金币数量" }}
          </label>
          <el-input-number
            v-model="form.value"
            :min="1"
            :max="99999"
            class="w-full !rounded-lg"
            :controls-position="''"
          >
            <template #prefix>
              <component
                :is="form.type === 'vip' ? Calendar : Coins"
                class="w-5 h-5 transition-transform duration-200"
              />
            </template>
          </el-input-number>
        </div>

        <!-- 生成数量 -->
        <div>
          <label class="text-sm text-gray-600 mb-2 block">生成数量</label>
          <el-input-number
            v-model="form.count"
            :min="1"
            :max="1000"
            class="w-full !rounded-lg"
            :controls-position="''"
          >
            <template #prefix>
              <Hash class="w-5 h-5" />
            </template>
          </el-input-number>
        </div>

        <!-- 过期时间 -->
        <div>
          <label class="text-sm text-gray-600 mb-2 block">过期时间</label>
          <el-date-picker
            v-model="form.expiredAt"
            type="datetime"
            placeholder="选择过期时间"
            class="w-full !rounded-lg"
          />
        </div>
      </div>

      <!-- 生成按钮 -->
      <div class="mt-6 flex justify-end">
        <el-button
          type="primary"
          :loading="generating"
          class="!rounded-lg !px-8 !h-10 transform transition-all duration-200 hover:scale-105"
          @click="handleGenerate"
        >
          <span class="text-base">{{
            generating ? "生成中..." : "生成卡密"
          }}</span>
        </el-button>
      </div>
    </div>

    <!-- 批次列表 -->
    <div class="bg-white rounded-3xl shadow-lg p-6">
      <div
        class="flex sm:items-center sm:justify-between flex-col sm:flex-row mb-6"
      >
        <div class="flex items-center">
          <div
            class="w-12 h-12 bg-green-100 rounded-2xl flex items-center justify-center mr-4"
          >
            <List class="w-6 h-6 text-green-500" />
          </div>
          <h2
            class="text-xl font-bold bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent"
          >
            卡密批次
          </h2>
        </div>
        <el-input
          v-model="searchQuery"
          placeholder="搜索批次..."
          class="w-full sm:w-64 !rounded-lg mt-4 sm:mt-0"
        >
          <template #prefix>
            <Search class="w-5 h-5" />
          </template>
        </el-input>
      </div>

      <!-- PC端表格布局 -->
      <div class="hidden sm:block">
        <el-table
          v-loading="loading"
          :data="filteredBatches"
          class="w-full"
          :class="{ 'opacity-75': loading }"
        >
          <el-table-column label="批次号" prop="batchNo" min-width="180">
            <template #default="{ row }">
              <div class="font-mono text-gray-600">{{ row.batchNo }}</div>
            </template>
          </el-table-column>

          <el-table-column label="类型" width="120">
            <template #default="{ row }">
              <el-tag
                :type="row.type === 'vip' ? 'warning' : 'success'"
                class="!rounded-full"
              >
                <div class="flex items-center">
                  <component
                    :is="row.type === 'vip' ? Crown : Coins"
                    class="w-4 h-4 mr-1"
                  />
                  {{ row.type === "vip" ? "VIP会员" : "金币" }}
                </div>
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="面值" width="120">
            <template #default="{ row }">
              <div class="font-bold">
                {{ row.value }}{{ row.type === "vip" ? "天" : "个" }}
              </div>
            </template>
          </el-table-column>

          <el-table-column label="使用情况" width="120">
            <template #default="{ row }">
              <el-progress
                :percentage="Math.round((row.usedCount / row.count) * 100)"
                :status="row.usedCount === row.count ? 'success' : ''"
                class="w-24"
              />
            </template>
          </el-table-column>

          <el-table-column label="过期时间" min-width="180">
            <template #default="{ row }">
              <div
                :class="[
                  'flex items-center',
                  { 'text-red-500': isExpired(row.expiredAt) },
                ]"
              >
                <Clock
                  class="w-4 h-4 mr-1"
                  :class="{ 'text-yellow-500': isAboutToExpire(row.expiredAt) }"
                />
                {{ formatDateTime(row.expiredAt) }}
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <div class="flex space-x-4">
                <el-button
                  type="primary"
                  link
                  class="!flex !items-center !gap-1 !px-3 !py-2 hover:!bg-blue-50 !rounded-lg"
                  @click="handleCopy(row.batchNo)"
                >
                  <Copy class="w-4 h-4" />
                  <span>复制</span>
                </el-button>
                <el-button
                  type="primary"
                  link
                  class="!flex !items-center !gap-1 !px-3 !py-2 hover:!bg-blue-50 !rounded-lg"
                  @click="handleViewDetails(row)"
                >
                  <Eye class="w-4 h-4" />
                  <span>详情</span>
                </el-button>
                <el-button
                  type="danger"
                  link
                  class="!flex !items-center !gap-1 !px-3 !py-2 hover:!bg-red-50 !rounded-lg"
                  @click="handleDeleteBatch(row)"
                >
                  <Trash2 class="w-4 h-4" />
                  <span>删除</span>
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 移动端卡片布局 -->
      <div class="sm:hidden space-y-4">
        <div
          v-for="batch in filteredBatches"
          :key="batch.batchNo"
          class="bg-gray-50 rounded-xl p-4 space-y-3"
        >
          <!-- 批次号和类型 -->
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <component
                :is="batch.type === 'vip' ? Crown : Coins"
                class="w-5 h-5"
                :class="
                  batch.type === 'vip' ? 'text-yellow-500' : 'text-amber-500'
                "
              />
              <span class="text-sm font-medium">
                {{ batch.type === "vip" ? "VIP会员" : "金币" }}
              </span>
            </div>
            <el-tag
              size="small"
              :type="isExpired(batch.expiredAt) ? 'danger' : 'success'"
              class="!rounded-full"
            >
              {{ isExpired(batch.expiredAt) ? "已过期" : "使用中" }}
            </el-tag>
          </div>

          <!-- 批次号 -->
          <div class="flex items-center justify-between">
            <div class="text-xs text-gray-500">批次号</div>
            <div class="font-mono text-sm">{{ batch.batchNo }}</div>
          </div>

          <!-- 面值和使用情况 -->
          <div class="grid grid-cols-3 gap-4">
            <div>
              <div class="text-xs text-gray-500 mb-1">面值</div>
              <div class="text-sm font-semibold">
                {{ batch.value }}{{ batch.type === "vip" ? "天" : "个" }}
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500 mb-1">使用情况</div>
              <div class="text-sm font-semibold">
                {{ batch.usedCount }}/{{ batch.count }}
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500 mb-1">过期时间</div>
              <div class="text-sm truncate">
                {{ formatDateTime(batch.expiredAt).split(" ")[0] }}
              </div>
            </div>
          </div>

          <!-- 进度条 -->
          <el-progress
            :percentage="Math.round((batch.usedCount / batch.count) * 100)"
            :status="batch.usedCount === batch.count ? 'success' : ''"
            :stroke-width="8"
            class="!mt-2"
          />

          <!-- 操作按钮 -->
          <div
            class="flex items-center justify-between pt-2 border-t border-gray-200"
          >
            <el-button
              type="primary"
              link
              class="!flex !items-center !gap-1"
              @click="handleCopy(batch.batchNo)"
            >
              <Copy class="w-4 h-4" />
              <span>复制</span>
            </el-button>

            <el-button
              type="primary"
              link
              class="!flex !items-center !gap-1"
              @click="handleViewDetails(batch)"
            >
              <Eye class="w-4 h-4" />
              <span>详情</span>
            </el-button>

            <el-button
              type="danger"
              link
              class="!flex !items-center !gap-1"
              @click="handleDeleteBatch(batch)"
            >
              <Trash2 class="w-4 h-4" />
              <span>删除</span>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailsVisible"
      :title="null"
      :width="isMobile ? '90%' : '800px'"
      :fullscreen="false"
      destroy-on-close
      :modal="true"
      :close-on-click-modal="true"
      class="!rounded-lg"
    >
      <!-- 弹窗头部 -->
      <template #header>
        <div class="flex items-center p-4 border-b border-gray-100">
          <div
            class="w-10 h-10 rounded-lg mr-3 flex items-center justify-center"
            :class="[
              selectedBatch?.type === 'vip' ? 'bg-yellow-100' : 'bg-green-100',
            ]"
          >
            <component
              :is="selectedBatch?.type === 'vip' ? Crown : Coins"
              class="w-6 h-6"
              :class="[
                selectedBatch?.type === 'vip'
                  ? 'text-yellow-500'
                  : 'text-green-500',
              ]"
            />
          </div>
          <div>
            <div class="text-xs text-gray-500">批次号</div>
            <div class="font-mono text-sm">{{ selectedBatch?.batchNo }}</div>
          </div>
        </div>
      </template>

      <!-- 弹窗内容 -->
      <div class="sm:hidden">
        <!-- 移动端卡片式列表 -->
        <div class="space-y-4 max-h-[60vh] overflow-y-auto">
          <div
            v-for="card in batchCards"
            :key="card.cardNo"
            class="bg-gray-50 rounded-lg p-4"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1 mr-2">
                <div class="font-mono text-sm break-all">{{ card.cardNo }}</div>
                <div class="flex items-center mt-2 space-x-2">
                  <el-tag
                    :type="card.isUsed ? 'info' : 'success'"
                    size="small"
                    class="!rounded-full"
                  >
                    {{ card.isUsed ? "已使用" : "未使用" }}
                  </el-tag>
                  <div class="text-xs text-gray-500">
                    {{ card.usedAt ? formatDateTime(card.usedAt) : "-" }}
                  </div>
                </div>
              </div>
              <el-button
                v-if="!card.isUsed"
                type="danger"
                link
                class="!flex !items-center !gap-1 !p-1"
                @click="handleDeleteCard(card.cardNo)"
              >
                <Trash2 class="w-4 h-4" />
              </el-button>
            </div>
          </div>

          <!-- 空状态 -->
          <div
            v-if="batchCards.length === 0"
            class="text-center py-8 text-gray-500"
          >
            暂无卡密数据
          </div>
        </div>
      </div>

      <!-- PC端表格 -->
      <div class="hidden sm:block">
        <el-table :data="batchCards" max-height="500">
          <el-table-column label="卡密" prop="cardNo" min-width="200">
            <template #default="{ row }">
              <div class="font-mono">{{ row.cardNo }}</div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag
                :type="row.isUsed ? 'info' : 'success'"
                class="!rounded-full"
              >
                {{ row.isUsed ? "已使用" : "未使用" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="使用时间" min-width="180">
            <template #default="{ row }">
              {{ row.usedAt ? formatDateTime(row.usedAt) : "-" }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="!row.isUsed"
                type="danger"
                link
                class="!flex !items-center !gap-1 hover:!bg-red-50 !rounded-lg"
                @click="handleDeleteCard(row.cardNo)"
              >
                <Trash2 class="w-4 h-4" />
                <span>删除</span>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 底部操作按钮 -->
      <template #footer>
        <div
          class="flex justify-between items-center p-4 border-t border-gray-100"
        >
          <el-button
            type="danger"
            class="!rounded-lg !w-[120px] !h-9"
            @click="handleDeleteBatch(selectedBatch)"
          >
            删除批次
          </el-button>
          <el-button
            type="primary"
            class="!rounded-lg !w-[120px] !h-9"
            @click="handleExportBatch"
          >
            导出批次
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { request } from "@/utils/request";
import {
  Wand2,
  Crown,
  Coins,
  Hash,
  Clock,
  Copy,
  Eye,
  Search,
  Calendar,
  List,
  Trash2,
} from "lucide-vue-next";

// 状态变量
const loading = ref(false);
const generating = ref(false);
const searchQuery = ref("");
const cardBatches = ref([]);
const detailsVisible = ref(false);
const selectedBatch = ref(null);
const batchCards = ref([]);
// 移动端检测
const isMobile = ref(window.innerWidth < 640);

// 监听窗口大小变化
onMounted(() => {
  window.addEventListener("resize", () => {
    isMobile.value = window.innerWidth < 640;
  });
});

onUnmounted(() => {
  window.removeEventListener("resize");
});
// 表单数据
const form = ref({
  type: "vip",
  value: 30,
  count: 10,
  expiredAt: "",
});

// 过滤后的批次列表
const filteredBatches = computed(() => {
  if (!searchQuery.value) return cardBatches.value;

  const query = searchQuery.value.toLowerCase();
  return cardBatches.value.filter(
    (batch) =>
      batch.batchNo.toLowerCase().includes(query) ||
      batch.type.toLowerCase().includes(query)
  );
});

// 生成卡密
const handleGenerate = async () => {
  if (generating.value) return;
  if (!form.value.value || !form.value.count) {
    ElMessage.warning({
      message: "请填写完整信息",
      plain: true,
    });
    return;
  }

  try {
    generating.value = true;

    // 构造请求数据为 JSON 格式
    const requestData = {
      type: form.value.type,
      value: form.value.value,
      count: form.value.count,
    };

    // 处理过期时间
    if (form.value.expiredAt) {
      requestData.expired_at = new Date(form.value.expiredAt).toISOString();
    }

    await request("/api/admin/cards", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    ElMessage.success({
      message: "生成成功",
      plain: true,
    });
    await fetchCardBatches();
  } catch (error) {
    console.error("生成卡密错误:", error);
    ElMessage.error({
      message: "生成失败",
      plain: true,
    });
  } finally {
    generating.value = false;
  }
};

// 删除单个卡密
const handleDeleteCard = async (cardNo) => {
  try {
    await ElMessageBox.confirm("确定要删除这个卡密吗？", "删除确认", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    await request(`/api/admin/cards/${cardNo}`, {
      method: "DELETE",
    });

    ElMessage.success({
      message: "删除成功",
      plain: true,
    });
    await refreshBatchDetails();
    await fetchCardBatches();
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除卡密错误:", error);
      ElMessage.error({
        message: "删除失败",
        plain: true,
      });
    }
  }
};

// 删除整个批次
const handleDeleteBatch = async (batch) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除批次 ${batch.batchNo} 吗？此操作将删除该批次下的所有未使用卡密。`,
      "删除确认",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    // 获取批次下所有卡密
    const cards = await request(`/api/admin/cards?batch_no=${batch.batchNo}`);

    // 删除所有未使用的卡密
    const deletePromises = cards
      .filter((card) => !card.is_used)
      .map((card) =>
        request(`/api/admin/cards/${card.card_no}`, {
          method: "DELETE",
        })
      );

    await Promise.all(deletePromises);

    ElMessage.success({
      message: "批次删除成功",
      plain: true,
    });
    if (detailsVisible.value) {
      detailsVisible.value = false;
    }
    await fetchCardBatches();
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除批次错误:", error);
      ElMessage.error({
        message: "删除失败",
        plain: true,
      });
    }
  }
};

// 复制卡密
const handleCopy = async (batchNo) => {
  try {
    const cards = await request(`/api/admin/cards?batch_no=${batchNo}`);
    const cardText = cards.map((card) => card.card_no).join("\n");
    await navigator.clipboard.writeText(cardText);
    ElMessage.success({
      message: "卡密已复制到剪贴板",
      plain: true,
      duration: 1500,
    });
  } catch (error) {
    console.error("复制卡密错误:", error);
    ElMessage.error({
      message: "复制失败",
      plain: true,
    });
  }
};

// 查看详情
const handleViewDetails = async (batch) => {
  try {
    selectedBatch.value = batch;
    await refreshBatchDetails();
    detailsVisible.value = true;
  } catch (error) {
    console.error("获取详情错误:", error);
    ElMessage.error({
      message: "获取详情失败",
      plain: true,
    });
  }
};

// 刷新批次详情
const refreshBatchDetails = async () => {
  if (!selectedBatch.value) return;
  try {
    const cards = await request(
      `/api/admin/cards?batch_no=${selectedBatch.value.batchNo}`
    );
    batchCards.value = cards.map((card) => ({
      cardNo: card.card_no,
      isUsed: card.is_used,
      usedAt: card.used_at,
    }));
  } catch (error) {
    console.error("刷新详情错误:", error);
    ElMessage.error({
      message: "刷新详情失败",
      plain: true,
    });
  }
};

// 导出批次
const handleExportBatch = async () => {
  if (!selectedBatch.value) return;
  try {
    const response = await request(
      `/api/admin/cards/export?batch_no=${selectedBatch.value.batchNo}`,
      {
        method: "GET",
        responseType: "blob",
      }
    );

    // 创建下载链接
    const blob = new Blob([response], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `cards-${selectedBatch.value.batchNo}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    ElMessage.success({
      message: "导出成功",
      plain: true,
    });
  } catch (error) {
    console.error("导出错误:", error);
    ElMessage.error({
      message: "导出失败",
      plain: true,
    });
  }
};

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return "永不过期";
  const d = new Date(date);
  return d.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
};

// 检查是否过期
const isExpired = (date) => {
  if (!date) return false;
  return new Date(date) < new Date();
};

// 检查是否即将过期（24小时内）
const isAboutToExpire = (date) => {
  if (!date) return false;
  const hours = (new Date(date) - new Date()) / (1000 * 60 * 60);
  return hours > 0 && hours < 24;
};

// 获取批次列表
const fetchCardBatches = async () => {
  loading.value = true;
  try {
    const cards = await request("/api/admin/cards");

    // 处理批次数据
    const batches = {};
    cards.forEach((card) => {
      if (!batches[card.batch_no]) {
        batches[card.batch_no] = {
          batchNo: card.batch_no,
          type: card.type,
          value: card.value,
          count: 0,
          usedCount: 0,
          expiredAt: card.expired_at,
        };
      }
      batches[card.batch_no].count++;
      if (card.is_used) {
        batches[card.batch_no].usedCount++;
      }
    });

    cardBatches.value = Object.values(batches).sort((a, b) =>
      b.batchNo.localeCompare(a.batchNo)
    );
  } catch (error) {
    console.error("获取批次列表错误:", error);
    ElMessage.error({
      message: "获取列表失败",
      plain: true,
    });
  } finally {
    loading.value = false;
  }
};

// 初始加载
fetchCardBatches();
</script>

<style scoped>
/* Element Plus 样式覆盖 */
:deep(.el-input__wrapper),
:deep(.el-select),
:deep(.el-input-number),
:deep(.el-date-editor) {
  @apply !border !border-gray-200 hover:!border-blue-500 focus:!border-blue-500 transition-colors;
}

:deep(.el-input-number__decrease),
:deep(.el-input-number__increase) {
  @apply !border-gray-200;
}

:deep(.el-dialog) {
  @apply !rounded-lg;
}

:deep(.el-dialog__header) {
  @apply !p-6 !mb-0 !border-b !border-gray-100;
}

:deep(.el-dialog__body) {
  @apply !p-6;
}

:deep(.el-dialog__footer) {
  @apply !p-6 !pt-4 !border-t !border-gray-100;
}

:deep(.el-table) {
  @apply !rounded-lg !overflow-hidden;
}

:deep(.el-table th) {
  @apply !bg-gray-50 !font-medium;
}

:deep(.el-table__row) {
  @apply hover:!bg-blue-50/50 transition-colors duration-200;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  @apply w-2;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded-full;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-300 rounded-full hover:bg-gray-400 transition-colors;
}

/* 统一圆角大小 */
.el-button,
.el-input,
.el-select,
.el-input-number,
.el-date-picker {
  @apply !rounded-lg;
}

/* 表格内操作按钮布局 */
.operations-container {
  @apply flex items-center space-x-2;
}

/* 进度条样式优化 */
:deep(.el-progress-bar__outer) {
  @apply !rounded-full;
}

:deep(.el-progress-bar__inner) {
  @apply !rounded-full transition-all duration-300;
}

/* 标签样式优化 */
:deep(.el-tag) {
  @apply !border-0 !shadow-sm;
}

/* 输入框控件优化 */
:deep(.el-input-number__decrease),
:deep(.el-input-number__increase) {
  @apply !border-gray-200 !transition-colors;
}

:deep(.el-input-number__decrease:hover),
:deep(.el-input-number__increase:hover) {
  @apply !bg-gray-50;
}

/* 按钮悬浮效果优化 */
:deep(.el-button:not(.is-disabled):hover) {
  @apply !opacity-90 !transform !scale-105 !transition-all;
}

/* 表格内标签动画 */
:deep(.el-tag) {
  @apply !transition-transform !duration-200;
}

:deep(.el-tag:hover) {
  @apply !transform !scale-105;
}

/* 输入框聚焦效果 */
:deep(.el-input__wrapper.is-focus),
:deep(.el-input.is-focus .el-input__wrapper) {
  @apply !ring-2 !ring-blue-500/20 !border-blue-500;
}

:deep(.el-overlay) {
  @apply !fixed !inset-0;
}

:deep(.el-dialog) {
  @apply !rounded-lg;
}

:deep(.el-dialog__header) {
  @apply !p-0 !m-0;
}

:deep(.el-dialog__headerbtn) {
  @apply !top-4 !right-4;
}

:deep(.el-dialog__body) {
  @apply !p-4;
}

:deep(.el-dialog__footer) {
  @apply !p-0 !m-0;
}

/* 确保蒙版在最顶层 */
:deep(.el-overlay) {
  @apply !z-50;
}

/* 确保弹窗位于蒙版上方 */
:deep(.el-dialog) {
  @apply !z-[51];
}

/* 添加蒙版动画 */
:deep(.el-overlay-dialog) {
  @apply !overflow-hidden !fixed !inset-0;
}
</style>
