<template>
  <div class="container mx-auto p-3 sm:p-4 max-w-4xl">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center min-h-screen">
      <el-loading :fullscreen="true" />
    </div>

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" show-icon class="mb-4" />

    <div v-if="!loading && !error" class="space-y-4 sm:space-y-6">
      <!-- 邀请人信息 -->
      <el-card v-if="inviter" class="!border-none shadow-md rounded-xl">
        <template #header>
          <div class="flex items-center px-2">
            <User class="w-5 h-5 mr-2 text-indigo-600" />
            <span class="text-base font-medium">邀请人信息</span>
          </div>
        </template>
        <div class="space-y-3 px-2">
          <p class="flex items-center text-gray-600">
            <User class="w-4 h-4 mr-2" />
            <span>邀请人:</span>
            <span class="ml-2 font-medium text-gray-900">{{
              inviter.username
            }}</span>
          </p>
          <p class="flex items-center text-gray-600">
            <Clock class="w-4 h-4 mr-2" />
            <span>邀请时间:</span>
            <span class="ml-2 font-medium text-gray-900">{{
              formatDate(inviter.invite_time)
            }}</span>
          </p>
          <p v-if="inviter.reward" class="flex items-center text-gray-600">
            <Gift class="w-4 h-4 mr-2" />
            <span>奖励:</span>
            <span class="ml-2 font-medium text-gray-900">
              {{ inviter.reward.amount }}
              {{ inviter.reward.type === "vip" ? "天VIP" : "金币" }}
            </span>
          </p>
        </div>
      </el-card>

      <!-- 邀请码卡片 -->
      <el-card class="!border-none shadow-md rounded-xl">
        <template #header>
          <div class="flex items-center px-2">
            <Share2 class="w-5 h-5 mr-2 text-indigo-600" />
            <span class="text-base font-medium">我的邀请链接</span>
          </div>
        </template>
        <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 px-2">
          <div class="bg-gray-50 p-3 rounded-lg flex-grow">
            <p class="font-mono text-sm sm:text-base text-gray-600 break-all">
              {{ generateInviteLink() }}
            </p>
          </div>
          <button
            @click="copyToClipboard"
            class="flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Copy v-if="!copied" class="w-4 h-4 mr-2" />
            <Check v-else class="w-4 h-4 mr-2" />
            {{ copied ? "已复制" : "复制链接" }}
          </button>
        </div>
      </el-card>

      <!-- 邀请统计 -->
      <el-card v-if="stats" class="!border-none shadow-md rounded-xl">
        <template #header>
          <div class="flex items-center px-2">
            <Users class="w-5 h-5 mr-2 text-indigo-600" />
            <span class="text-base font-medium">邀请统计</span>
          </div>
        </template>

        <!-- 统计数据 -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-6 px-2">
          <div class="bg-gray-50 p-4 rounded-xl">
            <div class="flex items-center mb-2">
              <Users class="w-4 h-4 mr-2 text-indigo-600" />
              <p class="text-sm text-gray-600">总邀请人数</p>
            </div>
            <p class="text-2xl font-bold text-indigo-600">
              {{ stats.total_invites }}
            </p>
          </div>
          <div class="bg-gray-50 p-4 rounded-xl">
            <div class="flex items-center mb-2">
              <Crown class="w-4 h-4 mr-2 text-indigo-600" />
              <p class="text-sm text-gray-600">VIP奖励天数</p>
            </div>
            <p class="text-2xl font-bold text-indigo-600">
              {{ stats.total_rewards.vip || 0 }}
            </p>
          </div>
          <div class="bg-gray-50 p-4 rounded-xl">
            <div class="flex items-center mb-2">
              <Coins class="w-4 h-4 mr-2 text-indigo-600" />
              <p class="text-sm text-gray-600">金币奖励</p>
            </div>
            <p class="text-2xl font-bold text-indigo-600">
              {{ stats.total_rewards.coin || 0 }}
            </p>
          </div>
        </div>

        <!-- 最近邀请记录 -->
        <div class="px-2">
          <div class="flex items-center mb-4">
            <Gift class="w-5 h-5 mr-2 text-indigo-600" />
            <span class="text-base font-medium">最近邀请记录</span>
          </div>

          <!-- 桌面端表格 -->
          <div class="hidden sm:block">
            <el-table :data="stats.recent_invites" style="width: 100%">
              <el-table-column label="用户名" min-width="120">
                <template #default="{ row }">
                  <div class="flex items-center">
                    <User class="w-4 h-4 mr-2 text-gray-500" />
                    {{ row.invitee_username }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="奖励类型" min-width="100">
                <template #default="{ row }">
                  <div class="flex items-center">
                    <component
                      :is="row.reward_type === 'vip' ? 'Crown' : 'Coins'"
                      class="w-4 h-4 mr-2 text-gray-500"
                    />
                    {{ row.reward_type === "vip" ? "VIP天数" : "金币" }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="reward_amount"
                label="奖励数量"
                min-width="100"
              />
              <el-table-column label="邀请时间" min-width="180">
                <template #default="{ row }">
                  <div class="flex items-center">
                    <Clock class="w-4 h-4 mr-2 text-gray-500" />
                    {{ formatDate(row.created_at) }}
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 移动端卡片列表 -->
          <div class="block sm:hidden space-y-3">
            <div
              v-for="(invite, index) in stats.recent_invites"
              :key="index"
              class="bg-gray-50 p-4 rounded-xl space-y-2"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <User class="w-4 h-4 mr-2 text-gray-500" />
                  <span class="font-medium">{{ invite.invitee_username }}</span>
                </div>
                <div class="flex items-center text-sm text-gray-500">
                  <component
                    :is="invite.reward_type === 'vip' ? 'Crown' : 'Coins'"
                    class="w-4 h-4 mr-1"
                  />
                  <span
                    >{{ invite.reward_amount }}
                    {{ invite.reward_type === "vip" ? "天" : "金币" }}</span
                  >
                </div>
              </div>
              <div class="flex items-center text-sm text-gray-500">
                <Clock class="w-4 h-4 mr-1" />
                {{ formatDate(invite.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import {
  User,
  Users,
  Share2,
  Copy,
  Check,
  Gift,
  Crown,
  Coins,
  Clock,
} from "lucide-vue-next";
import { request } from "@/utils/request";

// 响应式状态
const loading = ref(true);
const error = ref(null);
const inviteCode = ref("");
const inviter = ref(null);
const stats = ref(null);
const copied = ref(false);

// 获取所有数据
const fetchData = async () => {
  try {
    loading.value = true;
    await Promise.all([
      fetchInviteCode(),
      fetchInviterInfo(),
      fetchInviteStats(),
    ]);
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

// 获取邀请码
const fetchInviteCode = async () => {
  try {
    const res = await request("/api/users/invite-code", {
      method: "POST",
    });
    inviteCode.value = res.code;
  } catch (err) {
    console.error("Error fetching invite code:", err);
    ElMessage.error({
      message: "获取邀请码失败",
      plain: true,
    });
  }
};

// 获取邀请人信息
const fetchInviterInfo = async () => {
  try {
    const res = await request("/api/users/inviter");
    inviter.value = res.inviter;
  } catch (err) {
    console.error("Error fetching inviter info:", err);
    ElMessage.error({
      message: "获取邀请人信息失败",
      plain: true,
    });
  }
};

// 获取邀请统计
const fetchInviteStats = async () => {
  try {
    const res = await request("/api/users/invite-stats");
    stats.value = res;
  } catch (err) {
    console.error("Error fetching invite stats:", err);
    ElMessage.error({
      message: "获取邀请统计失败",
      plain: true,
    });
  }
};

// 生成邀请链接
const generateInviteLink = () => {
  const currentDomain = window.location.protocol + "//" + window.location.host;
  return `${currentDomain}/register?aff=${inviteCode.value}`;
};

// 复制到剪贴板
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(generateInviteLink());
    copied.value = true;
    ElMessage.success({
      message: "链接已复制到剪贴板",
      plain: true,
    });
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (err) {
    console.error("Failed to copy:", err);
    ElMessage.error({
      message: "复制失败",
      plain: true,
    });
  }
};

// 格式化日期
const formatDate = (date) => {
  if (!date) return "";
  return new Date(date).toLocaleString();
};

// 组件挂载时获取数据
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.container {
  margin: 0 auto;
}

:deep(.el-card__header) {
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

:deep(.el-card__body) {
  padding: 1rem;
}

@media (max-width: 640px) {
  :deep(.el-card__header) {
    padding: 0.875rem 1rem;
  }

  :deep(.el-card__body) {
    padding: 0.875rem 1rem;
  }
}
</style>
