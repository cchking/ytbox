<template>
  <div
    class="min-h-screen bg-gray-50 flex flex-col justify-center py-6 px-4 sm:py-12 sm:px-6 lg:px-8"
  >
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <!-- 标题区域 - 优化了移动端显示效果 -->
      <div class="text-center mb-4 sm:mb-6">
        <h1 class="text-3xl sm:text-4xl font-bold text-indigo-600">
          {{ settingsStore.title }}
        </h1>
        <h2
          class="mt-3 sm:mt-4 text-2xl sm:text-3xl font-extrabold text-gray-900"
        >
          创建新账号
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          已有账号？
          <router-link
            to="/login"
            class="font-medium text-indigo-600 hover:text-indigo-500 inline-block py-1"
          >
            立即登录
          </router-link>
        </p>
      </div>

      <!-- 注册表单卡片 - 优化了边距和圆角 -->
      <div
        class="bg-white py-6 sm:py-8 px-4 shadow-xl rounded-lg sm:rounded-lg sm:px-10"
      >
        <form class="space-y-5 sm:space-y-6" @submit.prevent="handleRegister">
          <!-- 用户名输入框 - 增加了移动端的触摸区域 -->
          <div>
            <label
              for="username"
              class="block text-sm font-medium text-gray-700"
            >
              用户名
            </label>
            <div class="mt-1">
              <input
                id="username"
                v-model="form.username"
                type="text"
                required
                class="appearance-none block w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base sm:text-sm"
                :class="{ 'border-red-500': errors.username }"
              />
              <p v-if="errors.username" class="mt-1 text-sm text-red-600">
                {{ errors.username }}
              </p>
            </div>
          </div>

          <!-- 邮箱输入框 -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
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

          <!-- 邮箱验证码 - 优化了按钮布局 -->
          <div v-if="requireEmailVerification">
            <div class="flex space-x-3">
              <div class="flex-1">
                <label
                  for="emailCode"
                  class="block text-sm font-medium text-gray-700"
                >
                  邮箱验证码
                </label>
                <div class="mt-1">
                  <input
                    id="emailCode"
                    v-model="form.emailCode"
                    type="text"
                    required
                    class="appearance-none block w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base sm:text-sm"
                    :class="{ 'border-red-500': errors.emailCode }"
                  />
                </div>
              </div>
              <div class="flex-none self-end">
                <button
                  type="button"
                  :disabled="countdown > 0 || !form.email"
                  @click="sendVerificationCode"
                  class="h-[46px] sm:h-[38px] px-3 sm:px-4 border border-gray-300 rounded-md text-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 whitespace-nowrap"
                >
                  {{ countdown > 0 ? `${countdown}s` : "获取验证码" }}
                </button>
              </div>
            </div>
            <p v-if="errors.emailCode" class="mt-1 text-sm text-red-600">
              {{ errors.emailCode }}
            </p>
          </div>

          <!-- 密码输入框 - 优化了图标触摸区域 -->
          <div>
            <label
              for="password"
              class="block text-sm font-medium text-gray-700"
            >
              密码
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

          <!-- 确认密码输入框 -->
          <div>
            <label
              for="confirmPassword"
              class="block text-sm font-medium text-gray-700"
            >
              确认密码
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

          <!-- 注册按钮 - 优化了按钮大小和加载状态 -->
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
              {{ loading ? "注册中..." : "立即注册" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Eye, EyeOff, Loader2 } from "lucide-vue-next";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";
import { useSettingsStore } from "@/stores/settings";
const router = useRouter();
const route = useRoute();
const loading = ref(false);
const showPassword = ref(false);
const requireEmailVerification = ref(false);
const countdown = ref(0);
const settingsStore = useSettingsStore();

const form = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  emailCode: "",
  inviteCode: "", // 保留此字段用于存储URL中的邀请码
});

const errors = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  emailCode: "",
});

// 获取系统设置
const getSystemSettings = async () => {
  try {
    const response = await request("/api/system/settings/public");
    requireEmailVerification.value = response.requireEmailVerification;

    if (!response.allowRegistration) {
      ElMessage.error({
        message: "系统当前未开放注册",
        plain: true,
      });
      router.push("/login");
    }
  } catch (error) {
    console.error("获取系统设置失败:", error);
    ElMessage.error({
      message: "获取系统设置失败",
      plain: true,
    });
  }
};

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
    const formData = new FormData();
    formData.append("email", form.email);

    await request("/api/users/send-verification-code", {
      method: "POST",
      body: formData,
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
    // 修改这里的错误处理逻辑
    if (error.response) {
      try {
        const errorData = await error.response.json();
        ElMessage.error(errorData.detail || "发送验证码失败");
      } catch (e) {
        ElMessage.error({
          message: "发送验证码失败",
          plain: true,
        });
      }
    } else {
      ElMessage.error({
        message: "发送验证码失败",
        plain: true,
      });
    }
  }
};

// 表单验证
const validateForm = () => {
  let isValid = true;
  errors.username = "";
  errors.email = "";
  errors.password = "";
  errors.confirmPassword = "";
  errors.emailCode = "";

  if (form.username.length < 3) {
    errors.username = "用户名至少需要3个字符";
    isValid = false;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(form.email)) {
    errors.email = "请输入有效的邮箱地址";
    isValid = false;
  }

  if (form.password.length < 6) {
    errors.password = "密码至少需要6个字符";
    isValid = false;
  }

  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = "两次输入的密码不一致";
    isValid = false;
  }

  if (requireEmailVerification.value && !form.emailCode) {
    errors.emailCode = "请输入邮箱验证码";
    isValid = false;
  }

  return isValid;
};

// 处理注册
const handleRegister = async () => {
  if (!validateForm()) return;

  loading.value = true;
  try {
    // 获取URL中的邀请码
    const inviteCode = form.inviteCode;

    // 构建请求URL
    let endpoint = "/api/users/register";
    if (inviteCode) {
      endpoint = `/api/users/register-with-invite?invite_code=${inviteCode}`;
      if (requireEmailVerification.value) {
        endpoint += `&email_code=${form.emailCode}`;
      }
    } else if (requireEmailVerification.value) {
      endpoint = `/api/users/register?email_code=${form.emailCode}`;
    }

    const response = await request(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: form.username,
        email: form.email,
        password: form.password,
      }),
    });

    ElMessage.success({
      message: "注册成功！",
      plain: true,
    });
    router.push("/login");
  } catch (error) {
    console.error({
      message: "注册失败:",
      error,
      plain: true,
    });
    if (error.response) {
      try {
        const errorData = await error.response.json();
        ElMessage.error({
          message: errorData.detail || "注册失败，请重试",
          plain: true,
        });
      } catch (e) {
        ElMessage.error({
          message: error.message || "注册失败，请重试",
          plain: true,
        });
      }
    } else {
      ElMessage.error({
        message: error.message || "注册失败，请重试",
        plain: true,
      });
    }
  } finally {
    loading.value = false;
  }
};

// 在组件挂载时获取URL中的邀请码和系统设置
onMounted(() => {
  getSystemSettings();
  const affCode = route.query.aff;
  if (affCode) {
    form.inviteCode = affCode;
  }
});
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
</style>
