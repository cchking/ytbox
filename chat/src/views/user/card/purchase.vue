<template>
  <NavBar title="充值" />
  <div class="container relative mx-auto max-w-4xl py-8 px-4">
    <!-- Loading Overlay -->
    <div
      v-if="loading"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div
        class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"
      ></div>
    </div>

    <!-- Title -->
    <div class="text-center mb-8">
      <h1
        class="text-2xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
      >
        卡密充值中心
      </h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">快速便捷的充值服务</p>
    </div>

    <div class="grid md:grid-cols-2 gap-6">
      <!-- Purchase Info Card -->
      <div
        class="group bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/10 dark:to-purple-900/10 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 relative overflow-hidden"
      >
        <div
          class="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
        ></div>

        <div class="relative z-10">
          <h2
            class="text-xl font-semibold text-blue-700 dark:text-blue-300 mb-6 flex items-center gap-2"
          >
            <CreditCard class="h-6 w-6" />
            购买说明
          </h2>

          <!-- Purchase Info -->
          <div
            class="bg-white/60 dark:bg-white/10 rounded-lg p-4 border border-blue-100 dark:border-blue-800 prose prose-sm max-w-none dark:prose-invert mb-4"
            v-if="purchaseInfo.description"
            v-html="formattedDescription"
          ></div>

          <!-- Action Button -->
          <div class="flex justify-end mt-6">
            <button
              @click="handleBuyClick"
              type="button"
              class="group inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-lg transition-all duration-300 shadow-md hover:shadow-lg cursor-pointer active:scale-95"
            >
              <ExternalLink
                class="h-4 w-4 group-hover:scale-110 transition-transform"
              />
              了解更多
            </button>
          </div>
        </div>
      </div>

      <!-- Redeem Card -->
      <div
        class="group bg-gradient-to-br from-pink-50 to-orange-50 dark:from-pink-900/10 dark:to-orange-900/10 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 relative overflow-hidden"
      >
        <div
          class="absolute inset-0 bg-gradient-to-r from-pink-500/10 to-orange-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
        ></div>

        <div class="relative z-10">
          <h2
            class="text-xl font-semibold text-pink-700 dark:text-pink-300 mb-6 flex items-center gap-2"
          >
            <Ticket class="h-6 w-6" />
            兑换卡密
          </h2>

          <div class="space-y-4">
            <!-- Redeem Input -->
            <div class="flex gap-3">
              <input
                v-model="cardNo"
                type="text"
                placeholder="请输入卡密"
                class="flex-1 rounded-lg border border-pink-200 dark:border-pink-800 bg-white/80 dark:bg-white/5 px-4 py-2 outline-none focus:ring-2 focus:ring-pink-500 dark:focus:ring-pink-600 focus:border-transparent transition-all duration-200"
              />
              <button
                @click="handleRedeem"
                :disabled="loading || !cardNo"
                class="px-6 py-2 bg-gradient-to-r from-pink-500 to-orange-500 hover:from-pink-600 hover:to-orange-600 disabled:from-gray-400 disabled:to-gray-400 text-white rounded-lg transition-all duration-300 disabled:cursor-not-allowed shadow-md hover:shadow-lg disabled:shadow-none"
              >
                <span class="flex items-center gap-2">
                  <RefreshCw v-if="loading" class="h-4 w-4 animate-spin" />
                  {{ loading ? "兑换中..." : "立即兑换" }}
                </span>
              </button>
            </div>

            <!-- Error Message -->
            <div
              v-if="error"
              class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg flex items-center gap-2"
            >
              <AlertCircle class="h-4 w-4 flex-shrink-0" />
              {{ error }}
            </div>

            <!-- Success Message with Animation -->
            <div
              v-if="success"
              class="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300 px-4 py-3 rounded-lg flex items-center gap-2"
            >
              <CheckCircle class="h-4 w-4 flex-shrink-0 text-green-500" />
              {{ success }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { request } from "@/utils/request";
import NavBar from "@/components/NavBar.vue";
import {
  CreditCard,
  Ticket,
  CheckCircle,
  ExternalLink,
  RefreshCw,
  AlertCircle,
} from "lucide-vue-next";

const cardNo = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");
const purchaseInfo = ref({ url: "", description: "" });

const formattedDescription = computed(() => {
  return purchaseInfo.value.description?.replace(/\n/g, "<br/>");
});

onMounted(async () => {
  try {
    const data = await request("/api/card-purchase-info");
    purchaseInfo.value = data;
  } catch (err) {
    ElMessage.error({
      message: "获取购买信息失败",
      plain: true,
    });
    console.error("Error fetching purchase info:", err);
  }
});

const handleBuyClick = () => {
  if (purchaseInfo.value.url) {
    window.open(purchaseInfo.value.url, "_blank");
  } else {
    ElMessage.warning({
      message: "购买链接未配置",
      plain: true,
    });
  }
};

const createStars = () => {
  const container = document.createElement("div");
  container.className = "stars-container";
  document.body.appendChild(container);

  for (let i = 0; i < 20; i++) {
    const star = document.createElement("div");
    star.className = "celebration-star";
    const delay = Math.random() * 0.5;
    star.style.left = `${Math.random() * 100}%`;
    star.style.animationDelay = `${delay}s`;
    container.appendChild(star);
  }

  setTimeout(() => container.remove(), 2000);
};

const handleRedeem = async () => {
  if (!cardNo.value.trim()) {
    error.value = "请输入卡密";
    return;
  }

  loading.value = true;
  error.value = "";
  success.value = "";

  try {
    const data = await request(`/api/cards/use/${cardNo.value}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    success.value = `兑换成功！获得 ${data.value} ${
      data.type === "vip" ? "天VIP会员" : "个金币"
    }`;
    cardNo.value = "";
    createStars();
    ElMessage.success({
      message: success.value,
      plain: true,
    });
  } catch (err) {
    // 401 错误会被 request 函数自动处理
    if (err.response) {
      const errorData = await err.response.json();
      error.value = errorData.detail || "兑换失败";
    } else {
      error.value = err.message || "兑换失败";
    }
    ElMessage.error({
      message: error.value,
      plain: true,
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.stars-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
}

.celebration-star {
  position: absolute;
  bottom: 0;
  width: 10px;
  height: 10px;
  background: #ffd700;
  clip-path: polygon(
    50% 0%,
    61% 35%,
    98% 35%,
    68% 57%,
    79% 91%,
    50% 70%,
    21% 91%,
    32% 57%,
    2% 35%,
    39% 35%
  );
  animation: float-up 2s ease-out forwards;
}

@keyframes float-up {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) rotate(360deg);
    opacity: 0;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .container {
    padding: 1rem;
  }

  .grid {
    gap: 1rem;
  }

  .text-2xl {
    font-size: 1.5rem;
  }

  .p-6 {
    padding: 1rem;
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
</style>
