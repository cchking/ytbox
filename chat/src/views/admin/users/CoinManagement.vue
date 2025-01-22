<template>
  <el-dialog
    v-model="dialogVisible"
    title="金币管理"
    :width="isMobile ? '90%' : '500px'"
    :close-on-click-modal="false"
    class="coin-modal"
    @closed="handleClose"
  >
    <div class="space-y-6">
      <!-- 金币余额展示 -->
      <div
        class="text-center p-4 bg-gradient-to-r from-yellow-50 to-amber-50 rounded-lg"
      >
        <div class="text-sm text-gray-600 mb-2">当前金币余额</div>
        <div class="flex items-center justify-center gap-2">
          <Coins class="w-6 h-6 text-yellow-500" />
          <div class="text-2xl font-bold text-yellow-500">
            {{ user?.coins || 0 }} 枚
          </div>
        </div>
      </div>

      <!-- 表单部分 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        :label-position="isMobile ? 'top' : 'right'"
        :label-width="isMobile ? 'auto' : '100px'"
      >
        <el-form-item label="操作类型" prop="type">
          <el-radio-group v-model="form.type" class="flex gap-4">
            <el-radio label="add">增加</el-radio>
            <el-radio label="subtract">减少</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="金币数量" prop="amount">
          <el-input-number
            v-model="form.amount"
            :min="1"
            :max="99999"
            class="!w-full"
            :controls-position="isMobile ? '' : 'right'"
          />
        </el-form-item>

        <el-form-item label="变更说明" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入金币变更原因"
            class="!resize-none"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <div class="flex justify-end gap-2">
        <el-button @click="handleClose"> 取消 </el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确认
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Coins } from "lucide-vue-next";

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close", "submit"]);

// 响应式状态
const dialogVisible = ref(true);
const submitting = ref(false);
const formRef = ref(null);
const isMobile = ref(false);

// 检测移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth < 640;
};

onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile);
});

const form = reactive({
  type: "add",
  amount: 100,
  description: "",
});

const rules = {
  type: [{ required: true, message: "请选择操作类型" }],
  amount: [{ required: true, message: "请输入金币数量" }],
  description: [{ required: true, message: "请输入变更说明" }],
};

const handleClose = () => {
  dialogVisible.value = false;
  emit("close");
};

const handleSubmit = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    submitting.value = true;

    const actualAmount = form.type === "add" ? form.amount : -form.amount;

    emit("submit", {
      amount: actualAmount,
      description: form.description,
    });
  } catch (error) {
    console.error("表单验证失败:", error);
    ElMessage.error({
      message: "请填写完整的表单信息",
      plain: true,
    });
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.coin-modal {
  position: relative;
  z-index: 2001 !important;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

/* 移动端样式优化 */
@media (max-width: 640px) {
  :deep(.el-form-item__label) {
    margin-bottom: 4px;
  }

  :deep(.el-input-number) {
    width: 100% !important;
  }

  :deep(.el-input-number .el-input__wrapper) {
    padding-left: 8px;
    padding-right: 8px;
  }
}
</style>
