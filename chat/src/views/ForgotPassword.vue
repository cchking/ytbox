<!-- ForgotPassword.vue -->
<template>
  <div
    class="min-h-screen bg-gray-50 flex flex-col justify-center py-6 px-4 sm:py-12 sm:px-6 lg:px-8"
  >
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <!-- 标题区域优化 -->
      <div class="text-center mb-4 sm:mb-6">
        <h1 class="text-3xl sm:text-4xl font-bold text-indigo-600">
          {{ settingsStore.title }}
        </h1>
        <h2
          class="mt-3 sm:mt-4 text-2xl sm:text-3xl font-extrabold text-gray-900"
        >
          找回密码
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          想起密码了？
          <router-link
            to="/login"
            class="font-medium text-indigo-600 hover:text-indigo-500 inline-block py-1"
          >
            立即登录
          </router-link>
        </p>
      </div>

      <!-- 重置密码表单卡片 -->
      <div
        class="bg-white py-6 sm:py-8 px-4 shadow-xl rounded-lg sm:rounded-lg sm:px-10"
      >
        <!-- 步骤提示器 -->
        <div class="mb-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
                :class="
                  step === 1
                    ? 'bg-indigo-600 text-white'
                    : 'bg-indigo-100 text-indigo-600'
                "
              >
                1
              </div>
              <div
                class="ml-2 text-sm font-medium"
                :class="step === 1 ? 'text-gray-900' : 'text-gray-500'"
              >
                验证身份
              </div>
            </div>
            <div class="flex-1 h-0.5 mx-4 bg-gray-200"></div>
            <div class="flex items-center">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
                :class="
                  step === 2
                    ? 'bg-indigo-600 text-white'
                    : 'bg-indigo-100 text-indigo-600'
                "
              >
                2
              </div>
              <div
                class="ml-2 text-sm font-medium"
                :class="step === 2 ? 'text-gray-900' : 'text-gray-500'"
              >
                设置密码
              </div>
            </div>
          </div>
        </div>

        <form class="space-y-5 sm:space-y-6" @submit.prevent="handleStep">
          <!-- 第一步: 邮箱和验证码 -->
          <template v-if="step === 1">
            <!-- 邮箱输入框 -->
            <div>
              <label
                for="email"
                class="block text-sm font-medium text-gray-700"
              >
                电子邮箱
              </label>
              <div class="mt-1">
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  required
                  class="appearance-none block w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base sm:text-sm"
                  :class="{ 'border-red-500': errors.email }"
                />
                <p v-if="errors.email" class="mt-1 text-sm text-red-600">
                  {{ errors.email }}
                </p>
              </div>
            </div>

            <!-- 验证码输入组 - 优化了移动端布局 -->
            <div>
              <div class="flex space-x-3">
                <div class="flex-1">
                  <label
                    for="code"
                    class="block text-sm font-medium text-gray-700"
                  >
                    验证码
                  </label>
                  <div class="mt-1">
                    <input
                      id="code"
                      v-model="form.code"
                      type="text"
                      required
                      class="appearance-none block w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base sm:text-sm"
                      :class="{ 'border-red-500': errors.code }"
                    />
                  </div>
                </div>
                <div class="flex-none self-end">
                  <button
                    type="button"
                    :disabled="countdown > 0 || !form.email"
                    @click="sendVerificationCode"
                    class="h-[46px] sm:h-[38px] px-3 sm:px-4 border border-gray-300 rounded-md text-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 whitespace-nowrap touch-manipulation"
                  >
                    {{ countdown > 0 ? `${countdown}s` : "获取验证码" }}
                  </button>
                </div>
              </div>
              <p v-if="errors.code" class="mt-1 text-sm text-red-600">
                {{ errors.code }}
              </p>
            </div>
          </template>

          <!-- 第二步: 设置新密码 -->
          <template v-else>
            <!-- 新密码输入框 -->
            <div>
              <label
                for="password"
                class="block text-sm font-medium text-gray-700"
              >
                新密码
              </label>
              <div class="mt-1 relative">
                <input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  class="appearance-none block w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base sm:text-sm"
                  :class="{ 'border-red-500': errors.password }"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 px-3 flex items-center touch-manipulation"
                  @click="showPassword = !showPassword"
                >
                  <Eye v-if="!showPassword" class="h-5 w-5 text-gray-400" />
                  <EyeOff v-else class="h-5 w-5 text-gray-400" />
                </button>
                <p v-if="errors.password" class="mt-1 text-sm text-red-600">
                  {{ errors.password }}
                </p>
              </div>
            </div>

            <!-- 确认新密码输入框 -->
            <div>
              <label
                for="confirmPassword"
                class="block text-sm font-medium text-gray-700"
              >
                确认新密码
              </label>
              <div class="mt-1">
                <input
                  id="confirmPassword"
                  v-model="form.confirmPassword"
                  type="password"
                  required
                  class="appearance-none block w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base sm:text-sm"
                  :class="{ 'border-red-500': errors.confirmPassword }"
                />
                <p
                  v-if="errors.confirmPassword"
                  class="mt-1 text-sm text-red-600"
                >
                  {{ errors.confirmPassword }}
                </p>
              </div>
            </div>
          </template>

          <!-- 提交按钮 -->
          <div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center py-3 sm:py-2 px-4 border border-transparent rounded-md shadow-sm text-base sm:text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              <Loader2
                v-if="loading"
                class="animate-spin -ml-1 mr-2 h-5 w-5 sm:h-4 sm:w-4 text-white"
              />
              {{ loading ? "处理中..." : buttonText }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue";
import { useRouter } from "vue-router";
import { Eye, EyeOff, Loader2 } from "lucide-vue-next";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";
import { useSettingsStore } from "@/stores/settings";
const router = useRouter();
const loading = ref(false);
const showPassword = ref(false);
const step = ref(1);
const countdown = ref(0);
const settingsStore = useSettingsStore();
const form = reactive({
  email: "",
  code: "",
  password: "",
  confirmPassword: "",
});

const errors = reactive({
  email: "",
  code: "",
  password: "",
  confirmPassword: "",
});

const buttonText = computed(() => {
  return step.value === 1 ? "下一步" : "重置密码";
});

// 发送验证码
const sendVerificationCode = async () => {
  if (!form.email) {
    errors.email = "请先输入邮箱地址";
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.email)) {
    errors.email = "请输入有效的邮箱地址";
    return;
  }

  try {
    await request("/api/reset-password/send-code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: form.email }),
    });

    ElMessage.success({
      message: "验证码已发送到邮箱",
      plain: true,
    });
    countdown.value = 60;
    const timer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);
  } catch (error) {
    ElMessage.error({
      message: error.message || "发送验证码失败",
      plain: true,
    });
  }
};

// 验证表单
const validateForm = () => {
  let isValid = true;

  if (step.value === 1) {
    errors.email = "";
    errors.code = "";

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(form.email)) {
      errors.email = "请输入有效的邮箱地址";
      isValid = false;
    }

    if (!form.code) {
      errors.code = "请输入验证码";
      isValid = false;
    }
  } else {
    errors.password = "";
    errors.confirmPassword = "";

    if (form.password.length < 6) {
      errors.password = "密码至少需要6个字符";
      isValid = false;
    }

    if (form.password !== form.confirmPassword) {
      errors.confirmPassword = "两次输入的密码不一致";
      isValid = false;
    }
  }

  return isValid;
};

// 处理表单提交
const handleStep = async () => {
  if (!validateForm()) return;

  loading.value = true;
  try {
    if (step.value === 1) {
      // 验证验证码
      step.value = 2;
    } else {
      // 重置密码
      await request("/api/reset-password/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: form.email,
          code: form.code,
          newPassword: form.password,
        }),
      });

      ElMessage.success({
        message: "密码重置成功！",
        plain: true,
      });
      router.push("/login");
    }
  } catch (error) {
    console.error("操作失败:", error);
    ElMessage.error({
      message: error.message || "操作失败，请重试",
      plain: true,
    });
    if (step.value === 2) {
      step.value = 1; // 如果重置密码失败，返回第一步
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 优化移动端触摸体验 */
@media (max-width: 640px) {
  input,
  button {
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
  }

  /* 优化移动端输入体验 */
  input {
    font-size: 16px; /* 防止 iOS 自动缩放 */
  }
}

/* 添加过渡动画 */
.step-enter-active,
.step-leave-active {
  transition: opacity 0.3s ease;
}

.step-enter-from,
.step-leave-to {
  opacity: 0;
}
</style>
