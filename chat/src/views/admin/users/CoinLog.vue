<template>
  <el-dialog
    v-model="dialogVisible"
    title="金币变动记录"
    :width="isMobile ? '95%' : '700px'"
    class="coin-log-modal"
    :center="true"
    :append-to-body="true"
    @closed="handleClose"
  >
    <!-- 移动端卡片布局 -->
    <div v-if="isMobile" class="space-y-3 max-h-80 overflow-y-auto">
      <div
        v-for="log in logData"
        :key="log.id"
        class="p-3 bg-gray-50 rounded-lg space-y-2"
      >
        <div class="flex items-center justify-between gap-2">
          <span class="text-xs text-gray-500">
            {{ formatDateTime(log.created_at) }}
          </span>
          <span
            :class="[
              log.amount >= 0 ? 'text-green-600' : 'text-red-600',
              'font-medium whitespace-nowrap',
            ]"
          >
            {{ log.amount >= 0 ? "+" : "" }}{{ log.amount }}
          </span>
        </div>
        <div class="flex items-start justify-between gap-3">
          <el-tag :type="getTypeTag(log.type)" size="small" class="shrink-0">
            {{ getTypeLabel(log.type) }}
          </el-tag>
          <span class="text-sm text-gray-600 text-right break-all">{{
            log.description
          }}</span>
        </div>
      </div>
    </div>

    <!-- 桌面端表格布局 -->
    <el-table
      v-else
      :data="logData"
      style="width: 100%"
      v-loading="loading"
      max-height="400"
    >
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column prop="amount" label="变动数量" width="120">
        <template #default="{ row }">
          <span
            :class="[
              row.amount >= 0 ? 'text-green-600' : 'text-red-600',
              'font-medium',
            ]"
          >
            {{ row.amount >= 0 ? "+" : "" }}{{ row.amount }}
          </span>
        </template>
      </el-table-column>

      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getTypeTag(row.type)" size="small">
            {{ getTypeLabel(row.type) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="description" label="说明" min-width="200" />
    </el-table>

    <template #footer>
      <div class="flex justify-end">
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";

const props = defineProps({
  userId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["close"]);
const dialogVisible = ref(true);
const loading = ref(false);
const logData = ref([]);

// 检测是否为移动端
const isMobile = ref(window.innerWidth < 640);

// 监听窗口大小变化
window.addEventListener("resize", () => {
  isMobile.value = window.innerWidth < 640;
});

const handleClose = () => {
  dialogVisible.value = false;
  emit("close");
};

const formatDateTime = (date) => {
  if (!date) return "";
  const d = new Date(date);
  return d.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
};

const getTypeTag = (type) => {
  const types = {
    admin: "warning",
    consume: "info",
    signin: "success",
    refund: "danger",
  };
  return types[type] || "info";
};

const getTypeLabel = (type) => {
  const labels = {
    admin: "管理员",
    consume: "消费",
    signin: "签到",
    refund: "退款",
  };
  return labels[type] || type;
};

const fetchLogs = async () => {
  loading.value = true;
  try {
    const data = await request(`/api/admin/users/${props.userId}/coin-logs`);
    logData.value = data;
  } catch (error) {
    ElMessage.error({
      message: "获取金币记录失败: " + error.message,
      plain: true,
    });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchLogs();
});
</script>

<style scoped>
.coin-log-modal {
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.el-dialog) {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  display: flex;
  flex-direction: column;
}

:deep(.el-dialog__body) {
  padding-top: 10px;
  padding-bottom: 10px;
}

/* 移动端样式优化 */
@media (max-width: 640px) {
  :deep(.el-dialog__body) {
    padding: 10px;
    max-height: calc(100vh - 120px);
    overflow-y: auto;
  }

  :deep(.el-dialog__footer) {
    padding: 10px;
    border-top: 1px solid #eee;
  }
}
</style>
