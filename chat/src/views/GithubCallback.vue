<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full px-6">
      <div class="text-center">
        <!-- 使用 GitHub 图标 -->
        <img
          src="@/assets/images/UilGithub.svg"
          class="mx-auto h-12 w-12 text-gray-900"
          alt="GitHub Logo"
        />
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
          GitHub 登录处理中
        </h2>
        <p class="mt-2 text-sm text-gray-600">{{ message }}</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="mt-8 flex justify-center">
        <Loader2 class="animate-spin h-8 w-8 text-gray-600" />
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mt-8 rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <XCircle class="h-5 w-5 text-red-400" />
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">登录失败</h3>
            <p class="mt-2 text-sm text-red-700">{{ error }}</p>
            <div class="mt-4">
              <button
                type="button"
                @click="goToLogin"
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                返回登录
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Loader2, XCircle } from "lucide-vue-next";
import { useUserStore } from "@/stores/user";
import { ElMessage } from "element-plus";

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const isLoading = ref(true);
const error = ref("");
const message = ref("正在处理 GitHub 登录请求...");

const goToLogin = () => {
  router.push("/login");
};

onMounted(async () => {
  const code = route.query.code;

  if (!code) {
    error.value = "未收到 GitHub 授权码";
    isLoading.value = false;
    return;
  }

  try {
    message.value = "正在验证 GitHub 授权...";
    const response = await fetch(`/api/auth/github/callback?code=${code}`, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "GitHub 登录验证失败");
    }

    const data = await response.json();
    console.log("GitHub 登录数据:", data);

    // 存储登录状态
    localStorage.setItem("accessToken", data.access_token);
    localStorage.setItem(
      "userInfo",
      JSON.stringify({
        id: data.id,
        username: data.username,
        email: data.email,
        role: data.role,
        is_active: data.is_active,
        vip_until: data.vip_until,
      })
    );

    // 更新 store
    userStore.setUserInfo({
      ...data,
      role: data.role.toLowerCase(),
    });

    ElMessage.success({
      message: "GitHub 登录成功",
      plain: true,
    });

    // 延迟跳转以确保数据保存完成
    setTimeout(() => {
      if (data.role.toLowerCase() === "admin") {
        router.push("/admin");
      } else {
        router.push("/chat");
      }
    }, 500);
  } catch (err) {
    console.error("GitHub OAuth回调错误:", err);
    error.value = err.message;
    isLoading.value = false;
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
</style>
