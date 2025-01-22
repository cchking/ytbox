<template>
  <div class="h-[30%] border-b p-4">
    <h2 class="text-xl font-bold mb-4">工具</h2>
    <div class="space-y-3">
      <button
        class="w-full px-4 py-2.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-600 font-medium transition-colors flex items-center justify-center gap-2"
        @click="$router.push('/console')"
      >
        <i class="fas fa-coins"></i>
        控制台充值
      </button>

      <button
        class="w-full px-4 py-2.5 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-600 font-medium transition-colors flex items-center justify-center gap-2"
        @click="$router.push('/purchase')"
      >
        <i class="fas fa-store"></i>
        充值商城
      </button>

      <button
        class="w-full px-4 py-2.5 rounded-lg bg-yellow-50 hover:bg-yellow-100 text-yellow-600 font-medium transition-colors flex items-center justify-center gap-2"
        @click="$router.push('/research')"
      >
        <i class="fas fa-flask"></i>
        研究所
      </button>

      <button
        class="w-full px-4 py-2.5 rounded-lg bg-gray-50 hover:bg-gray-100 text-gray-600 font-medium transition-colors flex items-center justify-center gap-2"
        @click="$router.push('/system/settings')"
      >
        <i class="fas fa-cog"></i>
        系统设置
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
const router = useRouter();
</script>
