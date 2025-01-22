<template>
  <div
    class="min-h-screen bg-gray-50 flex flex-col justify-center py-6 px-4 sm:py-12 sm:px-6 lg:px-8"
  >
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <!-- 标题区域 -->
      <div class="text-center mb-4 sm:mb-6">
        <h1 class="text-3xl sm:text-4xl font-bold text-indigo-600">
          {{ settingsStore.title }}
        </h1>
        <h2
          class="mt-3 sm:mt-4 text-2xl sm:text-3xl font-extrabold text-gray-900"
        >
          登录系统
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          还没有账号？
          <router-link
            to="/register"
            class="font-medium text-indigo-600 hover:text-indigo-500"
          >
            立即注册
          </router-link>
        </p>
      </div>

      <!-- 登录表单卡片 -->
      <div
        class="bg-white py-6 sm:py-8 px-4 shadow-xl rounded-lg sm:rounded-lg sm:px-10 mx-auto w-full sm:w-auto"
      >
        <form class="space-y-5 sm:space-y-6" @submit.prevent="handleLogin">
          <!-- 用户名输入框 -->
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
                type="text"
                v-model="formData.username"
                required
                class="appearance-none block w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base sm:text-sm"
              />
            </div>
          </div>

          <!-- 密码输入框 -->
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
                :type="showPassword ? 'text' : 'password'"
                v-model="formData.password"
                required
                class="appearance-none block w-full px-3 py-3 sm:py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base sm:text-sm"
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 pr-3 flex items-center touch-manipulation"
                @click="showPassword = !showPassword"
              >
                <Eye v-if="!showPassword" class="h-5 w-5 text-gray-400" />
                <EyeOff v-else class="h-5 w-5 text-gray-400" />
              </button>
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="rounded-md bg-red-50 p-3 sm:p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <XCircle class="h-5 w-5 text-red-400" />
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700">{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- 登录按钮 -->
          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-2.5 sm:py-2 px-4 border border-transparent rounded-md shadow-sm text-base sm:text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              <Loader2
                v-if="isLoading"
                class="animate-spin -ml-1 mr-2 h-5 w-5 sm:h-4 sm:w-4 text-white"
              />
              {{ isLoading ? "登录中..." : "登录" }}
            </button>
          </div>

          <!-- 第三方登录区域 -->
          <div class="mt-6">
            <div class="relative">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-300"></div>
              </div>
              <div class="relative flex justify-center text-sm">
                <span class="px-2 bg-white text-gray-500">第三方登录</span>
              </div>
            </div>

            <!-- 水平排列的第三方登录图标按钮 -->
            <div class="mt-6 flex justify-center space-x-4">
              <button
                type="button"
                @click="handleLinuxdoLogin"
                :disabled="isLoading"
                class="auth-icon-btn"
                title="Linux.do 账号登录"
              >
                <Loader2 v-if="isLoading" class="animate-spin w-6 h-6" />
                <img
                  v-else
                  src="@/assets/images/DeviconLinux.svg"
                  class="w-6 h-6"
                  alt="Linux.do"
                />
              </button>

              <!-- 新增 GitHub 登录按钮 -->
              <button
                type="button"
                @click="handleGithubLogin"
                :disabled="isLoading"
                class="auth-icon-btn"
                title="GitHub 账号登录"
              >
                <Loader2 v-if="isLoading" class="animate-spin w-6 h-6" />
                <img
                  v-else
                  src="@/assets/images/UilGithub.svg"
                  class="w-6 h-6"
                  alt="GitHub"
                />
              </button>
            </div>
          </div>

          <!-- 额外链接 -->
          <div class="flex items-center justify-end">
            <div class="text-sm">
              <router-link
                to="/forgot-password"
                class="font-medium text-indigo-600 hover:text-indigo-500 py-2 inline-block"
              >
                忘记密码？
              </router-link>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useUserStore } from "@/stores/user";
import { Eye, EyeOff, Loader2, XCircle } from "lucide-vue-next";
import { ElMessage } from "element-plus";
import { useSettingsStore } from "@/stores/settings";

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const settingsStore = useSettingsStore();

const formData = ref({
  username: "",
  password: "",
});

const error = ref("");
const isLoading = ref(false);
const showPassword = ref(false);

// 处理常规登录
const handleLogin = async () => {
  error.value = "";
  isLoading.value = true;

  try {
    console.log("尝试登录:", formData.value);

    const response = await fetch("/api/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        username: formData.value.username,
        password: formData.value.password,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "登录失败");
    }

    const data = await response.json();
    console.log("登录响应数据:", data);

    userStore.setUserInfo(data);

    ElMessage.success({
      message: "登录成功",
      plain: true,
    });

    if (userStore.isAdmin) {
      await router.push("/admin");
    } else {
      await router.push("/chat");
    }
  } catch (err) {
    console.error("登录错误:", err);
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
};

// 处理Linux.do登录
const handleLinuxdoLogin = async () => {
  try {
    const response = await fetch("/api/auth/linuxdo/login");
    const data = await response.json();
    window.location.href = data.url;
  } catch (err) {
    console.error("Linux.do登录错误:", err);
    error.value = "启动第三方登录失败";
  }
};

// 处理GitHub登录
const handleGithubLogin = async () => {
  try {
    const response = await fetch("/api/auth/github/login");
    const data = await response.json();
    window.location.href = data.url;
  } catch (err) {
    console.error("GitHub登录错误:", err);
    error.value = "启动GitHub登录失败";
  }
};

// 处理OAuth回调
onMounted(async () => {
  const code = route.query.code;
  const provider = route.query.provider; // 添加provider参数来区分登录源

  if (code) {
    isLoading.value = true;
    error.value = "";

    try {
      // 根据provider选择不同的回调端点
      const endpoint = provider === "github" ? "github" : "linuxdo";
      const response = await fetch(
        `/api/auth/${endpoint}/callback?code=${code}`
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "第三方登录失败");
      }

      const data = await response.json();
      userStore.setUserInfo(data);

      ElMessage.success({
        message: "登录成功",
        plain: true,
      });

      if (userStore.isAdmin) {
        await router.push("/admin");
      } else {
        await router.push("/chat");
      }
    } catch (err) {
      console.error("OAuth回调错误:", err);
      error.value = err.message;
    } finally {
      isLoading.value = false;
    }
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

.auth-icon-btn {
  @apply inline-flex items-center justify-center p-2 hover:opacity-80 transition-opacity;
}

.auth-icon-btn:active {
  @apply transform scale-95;
}

/* 优化移动端触摸体验 */
@media (max-width: 640px) {
  input,
  button {
    touch-action: manipulation;
  }
}
</style>
