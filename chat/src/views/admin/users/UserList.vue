<template>
  <div class="space-y-6">
    <!-- 数据总览卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <el-card
        shadow="hover"
        class="bg-gradient-to-br from-blue-50 to-blue-100"
      >
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-600">用户总数</div>
            <div class="text-2xl font-bold text-gray-900 mt-1">
              {{ stats.total_users || 0 }}
            </div>
          </div>
          <Users class="w-8 h-8 text-blue-600" />
        </div>
      </el-card>

      <el-card
        shadow="hover"
        class="bg-gradient-to-br from-purple-50 to-purple-100"
      >
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-600">VIP用户总数</div>
            <div class="text-2xl font-bold text-gray-900 mt-1">
              {{ stats.total_vip_users || 0 }}
            </div>
          </div>
          <Crown class="w-8 h-8 text-purple-600" />
        </div>
      </el-card>

      <el-card
        shadow="hover"
        class="bg-gradient-to-br from-green-50 to-green-100"
      >
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-600">今日新增用户</div>
            <div class="text-2xl font-bold text-gray-900 mt-1">
              {{ stats.today_new_users || 0 }}
            </div>
          </div>
          <UserPlus class="w-8 h-8 text-green-600" />
        </div>
      </el-card>

      <el-card
        shadow="hover"
        class="bg-gradient-to-br from-amber-50 to-amber-100"
      >
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-600">今日新增VIP</div>
            <div class="text-2xl font-bold text-gray-900 mt-1">
              {{ stats.today_new_vip_users || 0 }}
            </div>
          </div>
          <Star class="w-8 h-8 text-amber-600" />
        </div>
      </el-card>
    </div>

    <!-- 顶部搜索和添加 -->
    <div class="space-y-4">
      <div
        class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
      >
        <div>
          <h2 class="text-xl md:text-2xl font-bold text-gray-900">用户管理</h2>
          <p class="mt-1 text-sm text-gray-500">管理所有用户及其角色权限</p>
        </div>
        <el-button
          type="primary"
          class="bg-blue-600 w-full sm:w-auto"
          @click="openCreateModal"
        >
          <Plus class="w-4 h-4 mr-2" />添加用户
        </el-button>
      </div>

      <div
        class="bg-white rounded-lg shadow-sm border border-gray-200 flex items-center"
      >
        <Search class="w-5 h-5 mx-3 text-gray-400 hidden sm:block" />
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户名或邮箱..."
          class="flex-1 !border-none !shadow-none"
          clearable
          @input="handleSearch"
          @clear="clearSearch"
        />
      </div>
    </div>

    <!-- 移动端卡片布局 -->
    <div class="block lg:hidden space-y-4" v-loading="loading">
      <el-card
        v-for="user in users"
        :key="user.id"
        class="user-card relative overflow-visible"
        shadow="hover"
        :class="{ 'border-red-200': user.is_banned }"
      >
        <!-- 状态角标 -->
        <div
          v-if="user.is_banned"
          class="absolute -top-2 -right-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full"
        >
          已封禁
        </div>

        <div class="space-y-3">
          <!-- 用户基本信息 -->
          <div class="flex items-start gap-3">
            <div
              class="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-medium shrink-0"
              :class="{ 'from-red-500 to-red-600': user.is_banned }"
            >
              {{ user.username.charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-900 truncate">
                {{ user.username }}
              </div>
              <div class="text-sm text-gray-500 truncate">{{ user.email }}</div>
              <div class="text-sm text-yellow-600 flex items-center mt-1">
                <Coins class="w-4 h-4 mr-1 shrink-0" />
                <span class="truncate">{{ user.coins || 0 }} 金币</span>
              </div>
            </div>
          </div>

          <!-- 角色和VIP状态 -->
          <div class="flex items-center gap-2 flex-wrap">
            <el-tag
              :type="user.role === 'admin' ? 'danger' : 'primary'"
              size="small"
              :class="{ 'opacity-50': user.is_banned }"
            >
              {{ user.role === "admin" ? "管理员" : "普通用户" }}
            </el-tag>
            <span
              :class="[
                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                isVipActive(user.vip_until)
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800',
                user.is_banned ? 'opacity-50' : '',
              ]"
            >
              {{ isVipActive(user.vip_until) ? "VIP" : "普通会员" }}
            </span>
            <span v-if="user.vip_until" class="text-xs text-gray-500">
              {{ formatDate(user.vip_until) }}到期
            </span>
          </div>

          <!-- 操作按钮组 -->
          <div class="flex flex-wrap gap-2">
            <el-button type="primary" link @click="openEditModal(user)">
              <Edit class="w-4 h-4" />编辑
            </el-button>

            <el-button
              type="warning"
              link
              @click="openCoinModal(user)"
              :disabled="user.is_banned"
            >
              <Coins class="w-4 h-4" />金币
            </el-button>

            <el-button
              type="primary"
              link
              @click="openCoinLogModal(user)"
              :disabled="user.is_banned"
            >
              <History class="w-4 h-4" />记录
            </el-button>

            <el-button
              type="success"
              link
              @click="openVipModal(user)"
              :disabled="user.is_banned"
            >
              <Star class="w-4 h-4" />VIP
            </el-button>

            <el-button
              v-if="user.role !== 'admin'"
              :type="user.is_banned ? 'success' : 'danger'"
              link
              @click="handleToggleBan(user)"
            >
              <Lock class="w-4 h-4" />
              {{ user.is_banned ? "解封" : "封禁" }}
            </el-button>

            <el-button
              type="danger"
              link
              @click="handleDelete(user)"
              v-if="user.role !== 'admin'"
            >
              <Trash2 class="w-4 h-4" />删除
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 桌面端表格布局 -->
    <el-card class="hidden lg:block mb-6" v-loading="loading">
      <el-table :data="users" style="width: 100%" stripe>
        <!-- 用户信息列 -->
        <el-table-column label="用户信息" min-width="240">
          <template #default="{ row }">
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-medium"
                :class="{ 'from-red-500 to-red-600': row.is_banned }"
              >
                {{ row.username.charAt(0).toUpperCase() }}
              </div>
              <div class="flex flex-col">
                <div class="font-medium text-gray-900">{{ row.username }}</div>
                <div class="text-sm text-gray-500">{{ row.email }}</div>
                <div class="text-sm text-yellow-600 flex items-center mt-1">
                  <Coins class="w-4 h-4 mr-1" />
                  <span>{{ row.coins || 0 }} 金币</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 角色列 -->
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag
              :type="row.role === 'admin' ? 'danger' : 'primary'"
              size="small"
              :class="{ 'opacity-50': row.is_banned }"
            >
              {{ row.role === "admin" ? "管理员" : "普通用户" }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- VIP状态列 -->
        <el-table-column label="VIP状态" width="160">
          <template #default="{ row }">
            <div class="space-y-1">
              <div class="flex items-center">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    isVipActive(row.vip_until)
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800',
                    row.is_banned ? 'opacity-50' : '',
                  ]"
                >
                  {{ isVipActive(row.vip_until) ? "VIP" : "普通会员" }}
                </span>
              </div>
              <div v-if="row.vip_until" class="text-xs text-gray-500">
                {{ formatDate(row.vip_until) }}到期
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 操作列 -->
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="{ row }">
            <div class="flex gap-2">
              <el-button type="primary" link @click="openEditModal(row)">
                <Edit class="w-4 h-4" />编辑
              </el-button>

              <el-button
                type="warning"
                link
                @click="openCoinModal(row)"
                :disabled="row.is_banned"
              >
                <Coins class="w-4 h-4" />金币
              </el-button>

              <el-button
                type="primary"
                link
                @click="openCoinLogModal(row)"
                :disabled="row.is_banned"
              >
                <History class="w-4 h-4" />记录
              </el-button>

              <el-button
                type="success"
                link
                @click="openVipModal(row)"
                :disabled="row.is_banned"
              >
                <Star class="w-4 h-4" />VIP
              </el-button>

              <el-button
                v-if="row.role !== 'admin'"
                :type="row.is_banned ? 'success' : 'danger'"
                link
                @click="handleToggleBan(row)"
              >
                <Lock class="w-4 h-4" />
                {{ row.is_banned ? "解封" : "封禁" }}
              </el-button>

              <el-button
                type="danger"
                link
                @click="handleDelete(row)"
                v-if="row.role !== 'admin'"
              >
                <Trash2 class="w-4 h-4" />删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 用户表单对话框 -->
    <UserForm
      v-if="showCreateModal || showEditModal"
      :user="selectedUser"
      :is-edit="!!selectedUser"
      @close="closeUserModal"
      @submit="handleUserSubmit"
    />

    <!-- VIP管理对话框 -->
    <VipManagement
      v-if="showVipModal"
      :user="selectedUser"
      @close="closeVipModal"
      @submit="handleVipSubmit"
    />

    <!-- 金币管理对话框 -->
    <CoinManagement
      v-if="showCoinModal"
      :user="selectedUser"
      @close="closeCoinModal"
      @submit="handleCoinSubmit"
    />

    <!-- 金币记录对话框 -->
    <CoinLog
      v-if="showCoinLogModal"
      :user-id="selectedUser?.id"
      @close="closeCoinLogModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessageBox, ElMessage } from "element-plus";
import {
  Plus,
  Search,
  Edit,
  Star,
  Lock,
  Trash2,
  Coins,
  History,
  Users,
  UserPlus,
  Crown,
} from "lucide-vue-next";
import { request } from "@/utils/request";
import UserForm from "./UserForm.vue";
import VipManagement from "./VipManagement.vue";
import CoinManagement from "./CoinManagement.vue";
import CoinLog from "./CoinLog.vue";

// 状态变量定义
const users = ref([]);
const loading = ref(false);
const stats = ref({
  total_users: 0,
  total_vip_users: 0,
  today_new_users: 0,
  today_new_vip_users: 0,
});
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showVipModal = ref(false);
const showCoinModal = ref(false);
const showCoinLogModal = ref(false);
const selectedUser = ref(null);
const searchQuery = ref("");
let searchDebounce = null;

// 格式化日期函数
const formatDate = (date) => {
  if (!date) return "";
  const d = new Date(date);
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
};

// VIP状态检查
const isVipActive = (vipUntil) => {
  if (!vipUntil) return false;
  return new Date(vipUntil) > new Date();
};

// 获取用户统计数据
const fetchStats = async () => {
  try {
    const data = await request("/api/admin/users/stats");
    stats.value = data;
  } catch (error) {
    ElMessage.error({
      message: "获取统计数据失败: " + error.message,
      plain: true,
    });
  }
};

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true;
  try {
    const data = await request("/api/admin/users");
    users.value = data;
  } catch (error) {
    ElMessage.error({
      message: "获取用户列表失败: " + error.message,
      plain: true,
    });
  } finally {
    loading.value = false;
  }
};

// 搜索处理
const handleSearch = () => {
  if (searchDebounce) clearTimeout(searchDebounce);
  searchDebounce = setTimeout(async () => {
    loading.value = true;
    try {
      const data = await request(
        `/api/admin/users/search?query=${searchQuery.value}`
      );
      users.value = data;
    } catch (error) {
      ElMessage.error({
        message: "搜索失败: " + error.message,
        plain: true,
      });
    } finally {
      loading.value = false;
    }
  }, 300);
};

const clearSearch = () => {
  searchQuery.value = "";
  fetchUsers();
};

// 模态框操作
const openCreateModal = () => {
  selectedUser.value = null;
  showCreateModal.value = true;
};

const openEditModal = (user) => {
  selectedUser.value = user;
  showEditModal.value = true;
};

const openVipModal = (user) => {
  selectedUser.value = user;
  showVipModal.value = true;
};

const openCoinModal = (user) => {
  selectedUser.value = user;
  showCoinModal.value = true;
};

const openCoinLogModal = (user) => {
  selectedUser.value = user;
  showCoinLogModal.value = true;
};

const closeUserModal = () => {
  showCreateModal.value = false;
  showEditModal.value = false;
  selectedUser.value = null;
};

const closeVipModal = () => {
  showVipModal.value = false;
  selectedUser.value = null;
};

const closeCoinModal = () => {
  showCoinModal.value = false;
  selectedUser.value = null;
};

const closeCoinLogModal = () => {
  showCoinLogModal.value = false;
  selectedUser.value = null;
};

// 用户操作处理
const handleUserSubmit = async (userData) => {
  try {
    const url = selectedUser.value
      ? `/api/admin/users/${selectedUser.value.id}`
      : "/api/admin/users";

    await request(url, {
      method: selectedUser.value ? "PUT" : "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    ElMessage.success({
      message: selectedUser.value ? "更新成功" : "创建成功",
      plain: true,
    });
    closeUserModal();
    await Promise.all([fetchUsers(), fetchStats()]);
  } catch (error) {
    ElMessage.error({
      message: error.message,
      plain: true,
    });
  }
};

const handleToggleBan = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要${user.is_banned ? "解除封禁" : "封禁"}用户 "${
        user.username
      }" 吗？`,
      "确认操作",
      {
        confirmButtonText: user.is_banned ? "解除封禁" : "封禁",
        cancelButtonText: "取消",
        type: user.is_banned ? "success" : "warning",
      }
    );

    await request(`/api/admin/users/${user.id}/ban`, {
      method: "PATCH",
    });

    ElMessage.success({
      message: user.is_banned ? "用户已解除封禁" : "用户已被封禁",
      plain: true,
    });
    await Promise.all([fetchUsers(), fetchStats()]);
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error({
        message: "操作失败: " + error.message,
        plain: true,
      });
    }
  }
};

const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`,
      "警告",
      {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "error",
      }
    );

    await request(`/api/admin/users/${user.id}`, {
      method: "DELETE",
    });

    ElMessage.success({
      message: "删除成功",
      plain: true,
    });
    await Promise.all([fetchUsers(), fetchStats()]);
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error({
        message: "删除失败: " + error.message,
        plain: true,
      });
    }
  }
};

const handleVipSubmit = async (vipData) => {
  try {
    await request(`/api/admin/users/${selectedUser.value.id}/vip`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(vipData),
    });

    ElMessage.success({
      message: "VIP状态更新成功",
      plain: true,
    });
    closeVipModal();
    await Promise.all([fetchUsers(), fetchStats()]);
  } catch (error) {
    ElMessage.error({
      message: error.message,
      plain: true,
    });
  }
};

const handleCoinSubmit = async (coinData) => {
  try {
    // 将数据拼接到URL中作为查询参数
    const params = new URLSearchParams({
      amount: coinData.amount.toString(),
      description: coinData.description,
    });

    await request(
      `/api/admin/users/${selectedUser.value.id}/coins?${params.toString()}`,
      {
        method: "POST",
      }
    );

    ElMessage.success({
      message: "金币操作成功",
      plain: true,
    });
    closeCoinModal();
    await Promise.all([fetchUsers(), fetchStats()]);
  } catch (error) {
    ElMessage.error({
      message: error.message,
      plain: true,
    });
  }
};

// 初始化
onMounted(() => {
  Promise.all([fetchUsers(), fetchStats()]);
});
</script>

<style scoped>
.user-card {
  transition: all 0.3s ease;
}

.user-card:hover {
  transform: translateY(-2px);
}

/* 确保按钮图标对齐 */
:deep(.el-button--link) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* 调整表格内容垂直对齐 */
:deep(.el-table .cell) {
  display: flex;
  align-items: center;
}

/* 自定义滚动条样式 */
:deep(.el-table__body-wrapper::-webkit-scrollbar) {
  width: 6px;
  height: 6px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
  background: #dcdfe6;
  border-radius: 3px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
  background: #f5f7fa;
}

/* 移动端适配 */
@media (max-width: 640px) {
  :deep(.el-button) {
    padding: 8px 12px;
  }

  :deep(.el-table) {
    font-size: 14px;
  }
}

/* 弹窗层级管理 */
:deep(.coin-modal) {
  position: relative;
  z-index: 2001 !important;
}

:deep(.el-dialog__wrapper) {
  z-index: 2001 !important;
}

:deep(.el-table),
:deep(.el-table__body),
:deep(.el-table__header),
:deep(.el-table__body-wrapper),
:deep(.el-table__header-wrapper) {
  z-index: 0 !important;
}

:deep(.el-overlay) {
  z-index: 2000 !important;
}
</style>
