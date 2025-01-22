<template>
  <div class="h-[100%] border-b p-4">
    <h2 class="text-xl font-bold mb-4">用户详情</h2>
    <div v-if="loading" class="flex items-center">
      <div class="w-12 h-12 bg-gray-200 rounded-full mr-3 animate-pulse"></div>
      <div>
        <div class="h-4 w-24 bg-gray-200 rounded animate-pulse mb-2"></div>
        <div class="h-4 w-16 bg-gray-200 rounded animate-pulse"></div>
      </div>
    </div>
    <div v-else-if="error" class="text-red-500">加载用户信息失败</div>
    <div v-else>
      <!-- 用户基本信息 -->
      <div class="flex items-center">
        <div
          class="w-12 h-12 bg-indigo-600 rounded-full mr-3 flex items-center justify-center text-white text-xl"
          :class="{ 'bg-red-500': userInfo.is_banned }"
        >
          {{
            userInfo.username ? userInfo.username.charAt(0).toUpperCase() : "?"
          }}
        </div>
        <div>
          <p class="font-semibold">{{ userInfo.username }}</p>
          <p class="text-gray-600">{{ userInfo.email }}</p>
          <!-- 用户身份和金币标签并排显示 -->
          <div class="flex items-center mt-1 space-x-2">
            <!-- 用户身份标签 -->
            <span
              class="px-2 py-0.5 text-xs rounded-full"
              :class="[
                userInfo.role === 'admin'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-blue-100 text-blue-800',
                userInfo.is_banned ? 'opacity-50' : '',
              ]"
            >
              {{ userInfo.role === "admin" ? "管理员" : "普通用户" }}
            </span>
            <!-- 金币数量 -->
            <div class="flex items-center text-yellow-600">
              <Coins class="w-4 h-4 mr-1" />
              <span class="text-sm">{{ userInfo.coins || 0 }} 金币</span>
            </div>
          </div>
          <!-- VIP状态和封禁状态 -->
          <div class="flex items-center mt-1 space-x-2">
            <span
              v-if="userInfo.vip_until"
              class="px-2 py-0.5 text-xs rounded-full bg-yellow-100 text-yellow-800"
              :class="{ 'opacity-50': userInfo.is_banned }"
            >
              VIP ({{ formatVipDate(userInfo.vip_until) }})
            </span>
            <span
              v-if="userInfo.is_banned"
              class="px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-800"
            >
              已封禁
            </span>
          </div>
        </div>
      </div>

      <!-- 操作按钮区域 -->
      <div class="mt-4 flex space-x-2">
        <!-- 签到按钮/状态 -->
        <template v-if="userInfo.signin_enabled && !userInfo.is_banned">
          <button
            v-if="!userInfo.today_signed"
            @click="handleSignin"
            :disabled="signingIn"
            class="flex-1 flex items-center justify-center px-4 py-2 text-sm bg-green-500 text-white hover:bg-green-600 rounded-md transition-colors disabled:opacity-50"
          >
            <CalendarPlus class="w-4 h-4 mr-2" />
            {{ signingIn ? "签到中..." : "每日签到" }}
            <!-- <span v-if="userInfo.signin_reward_type" class="ml-1 text-xs">
              ({{
                userInfo.signin_reward_type === "coin"
                  ? `${userInfo.signin_reward_amount}金币`
                  : `${userInfo.signin_reward_amount}天VIP`
              }})
            </span> -->
          </button>
          <div
            v-else
            class="flex-1 flex items-center justify-center px-4 py-2 text-sm text-green-600 bg-green-50 rounded-md"
          >
            <CalendarCheck class="w-4 h-4 mr-2" />
            今日已签到
          </div>
        </template>

        <!-- 退出按钮 -->
        <button
          @click="handleLogout"
          class="flex-1 flex items-center justify-center px-4 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
        >
          <LogOut class="w-4 h-4 mr-2" />
          退出登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { request } from "@/utils/request";
import { LogOut, Coins, CalendarCheck, CalendarPlus } from "lucide-vue-next";
import { ElMessage } from "element-plus";

const router = useRouter();
const userStore = useUserStore();

// 状态管理
const loading = ref(true);
const error = ref(null);
const userInfo = ref({});
const signingIn = ref(false);

// 格式化 VIP 到期时间
const formatVipDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = date - now;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays <= 0) {
    return "已过期";
  }
  return `剩余 ${diffDays} 天`;
};

// 获取用户信息
async function fetchUserInfo() {
  try {
    loading.value = true;
    const data = await request("/api/users/me");
    userInfo.value = data;
  } catch (err) {
    console.error("获取用户信息失败:", err);
    error.value = err;
  } finally {
    loading.value = false;
  }
}

// 处理签到
const handleSignin = async () => {
  if (signingIn.value || userInfo.value.is_banned) return;

  try {
    signingIn.value = true;
    const response = await request("/api/signin", {
      method: "POST",
    });

    // 显示签到成功提示
    const rewardText =
      response.reward_type === "coin"
        ? `${response.reward_amount}金币`
        : `${response.reward_amount}天VIP`;
    ElMessage.success({
      message: `签到成功！获得${rewardText}`,
      plain: true,
    });

    // 重新加载用户信息以更新状态
    await fetchUserInfo();
  } catch (error) {
    if (error.response?.status === 400) {
      ElMessage.warning({
        message: "今天已经签到过了",
        plain: true,
      });
    } else {
      ElMessage.error({
        message: "签到失败，请重试",
        plain: true,
      });
    }
  } finally {
    signingIn.value = false;
  }
};

// 处理退出登录
const handleLogout = async () => {
  try {
    userStore.clearUserInfo();
    ElMessage.success({
      message: "退出成功",
      plain: true,
    });
    await router.push("/login");
  } catch (error) {
    console.error("退出失败:", error);
    ElMessage.error({
      message: "退出失败，请重试",
      plain: true,
    });
  }
};

// 页面加载时获取用户信息
onMounted(fetchUserInfo);
</script>
