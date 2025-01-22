<template>
  <el-dialog
    title="VIP管理"
    v-model="dialogVisible"
    :width="isMobile ? '90%' : '500px'"
    :center="true"
    :append-to-body="true"
    :close-on-click-modal="false"
    class="vip-dialog"
    @closed="$emit('close')"
  >
    <!-- 当前VIP状态 -->
    <div class="mb-6 p-4 bg-gray-50 rounded-lg">
      <div class="text-sm text-gray-600">当前状态</div>
      <div class="mt-1 font-medium" :class="vipStatusClass">
        {{ vipStatusText }}
      </div>
    </div>

    <!-- 操作表单 -->
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      :label-position="isMobile ? 'top' : 'right'"
      :label-width="isMobile ? 'auto' : '100px'"
      class="space-y-4"
    >
      <el-form-item label="操作类型" prop="operation">
        <el-select v-model="formData.operation" class="w-full">
          <el-option label="增加天数" value="add" />
          <el-option label="减少天数" value="subtract" />
          <el-option label="设置到期时间" value="set" />
        </el-select>
      </el-form-item>

      <template v-if="formData.operation !== 'set'">
        <el-form-item label="天数" prop="days">
          <el-input-number
            v-model="formData.days"
            :min="1"
            :max="999"
            class="!w-full"
            :controls-position="isMobile ? '' : 'right'"
          />
        </el-form-item>
      </template>

      <template v-else>
        <el-form-item label="到期时间" prop="expireDate">
          <el-date-picker
            v-model="formData.expireDate"
            type="date"
            class="!w-full"
            :min="tomorrow"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <div class="flex justify-end gap-2">
        <el-button @click="$emit('close')">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确认修改</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close", "submit"]);
const formRef = ref(null);
const dialogVisible = ref(true);
const isMobile = ref(false);

const formData = ref({
  operation: "add",
  days: 1,
  expireDate: "",
});

const rules = {
  operation: [{ required: true, message: "请选择操作类型" }],
  days: [{ required: true, message: "请输入天数" }],
  expireDate: [{ required: true, message: "请选择到期时间" }],
};

// 计算明天的日期作为最小可选日期
const tomorrow = computed(() => {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  return date.toISOString().split("T")[0];
});

// 计算VIP状态显示
const vipStatusText = computed(() => {
  if (!props.user.vip_until) return "非VIP用户";
  const vipUntil = new Date(props.user.vip_until);
  const now = new Date();
  if (vipUntil > now) {
    return `VIP用户 (到期时间：${vipUntil.toLocaleDateString()})`;
  }
  return "VIP已过期";
});

// VIP状态样式
const vipStatusClass = computed(() => {
  if (!props.user.vip_until) return "text-gray-900";
  const vipUntil = new Date(props.user.vip_until);
  const now = new Date();
  return vipUntil > now ? "text-green-600" : "text-red-600";
});

// 检测移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth < 640;
};

onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkMobile);
});

const handleSubmit = () => {
  if (!formRef.value) return;

  const data = {
    userId: props.user.id,
    operation: formData.value.operation,
  };

  if (formData.value.operation === "set") {
    data.expireDate = formData.value.expireDate;
  } else {
    data.days = formData.value.days;
  }

  emit("submit", data);
};
</script>

<style scoped>
.vip-dialog {
  position: relative;
  z-index: 2001 !important;
}

:deep(.el-dialog) {
  margin: 0 !important;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

/* 移动端样式优化 */
@media (max-width: 640px) {
  :deep(.el-dialog__body) {
    padding: 15px;
    max-height: calc(100vh - 120px);
    overflow-y: auto;
  }

  :deep(.el-form-item__label) {
    margin-bottom: 4px;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 15px;
  }

  :deep(.el-form-item) {
    margin-bottom: 15px;
  }

  :deep(.el-input-number) {
    width: 100% !important;
  }

  :deep(.el-input-number .el-input__wrapper) {
    padding-left: 8px;
    padding-right: 8px;
  }

  :deep(.el-input__wrapper) {
    padding: 0 11px;
  }

  :deep(.el-input__inner) {
    height: 36px;
  }

  :deep(.el-button) {
    padding: 8px 15px;
  }

  :deep(.el-select) {
    width: 100%;
  }

  :deep(.el-date-picker) {
    width: 100%;
  }
}
</style>
