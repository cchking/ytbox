<template>
  <el-dialog
    :title="isEdit ? '编辑用户' : '创建用户'"
    v-model="dialogVisible"
    :width="isMobile ? '95%' : '500px'"
    :center="true"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      :label-width="isMobile ? '60px' : '80px'"
      :label-position="isMobile ? 'top' : 'right'"
      class="space-y-4"
    >
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="formData.username"
          :disabled="isEdit"
          placeholder="请输入用户名"
        />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input
          v-model="formData.email"
          type="email"
          placeholder="请输入邮箱"
        />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="formData.password"
          type="password"
          :placeholder="isEdit ? '留空表示不修改' : '请输入密码'"
          show-password
        />
      </el-form-item>

      <el-form-item label="角色" prop="role">
        <el-select v-model="formData.role" class="w-full">
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="flex justify-end space-x-2">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? "保存" : "创建" }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";

const props = defineProps({
  user: {
    type: Object,
    default: null,
  },
  isEdit: {
    type: Boolean,
    default: false,
  },
});

// 检测是否为移动端
const isMobile = ref(window.innerWidth < 640);

// 监听窗口大小变化
window.addEventListener("resize", () => {
  isMobile.value = window.innerWidth < 640;
});

const emit = defineEmits(["close", "submit"]);
const formRef = ref(null);
const submitting = ref(false);
const dialogVisible = ref(true);

const formData = reactive({
  username: "",
  email: "",
  password: "",
  role: "user",
});

const rules = computed(() => ({
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
  password: props.isEdit
    ? []
    : [{ required: true, message: "请输入密码", trigger: "blur" }],
  role: [{ required: true, message: "请选择角色", trigger: "change" }],
}));

onMounted(() => {
  if (props.user) {
    Object.assign(formData, {
      username: props.user.username,
      email: props.user.email,
      password: "",
      role: props.user.role,
    });
  }
});

const handleClose = () => {
  dialogVisible.value = false;
  emit("close");
};

const handleSubmit = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    submitting.value = true;

    const submitData = { ...formData };
    if (props.isEdit && !submitData.password) {
      delete submitData.password;
    }

    emit("submit", submitData);
  } catch (error) {
    ElMessage.error({
      message: "请检查表单内容",
      plain: true,
    });
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
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

  :deep(.el-dialog__footer) {
    padding: 10px 15px;
  }

  :deep(.el-form-item__label) {
    padding-bottom: 4px;
    line-height: 1.2;
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
}
</style>
