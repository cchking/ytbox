<template>
  <div class="w-full h-full">
    <Doughnut :data="chartData" :options="chartOptions" :plugins="plugins" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from "vue";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Doughnut } from "vue-chartjs";

ChartJS.register(ArcElement, Tooltip, Legend);

interface ChartDataItem {
  label: string;
  value: number;
}

interface Props {
  data: ChartDataItem[];
  title?: string;
}

const props = defineProps<Props>();

// 使用与设计完全一致的颜色
const colors = [
  "rgba(59, 130, 246, 0.7)", // Blue - 主色
  "rgba(16, 185, 129, 0.7)", // Green - 次要色
  "rgba(245, 158, 11, 0.7)", // Yellow - 警告色
  "rgba(239, 68, 68, 0.7)", // Red - 危险色
  "rgba(139, 92, 246, 0.7)", // Purple - 点缀色
];

const isMobile = ref(false);

// 检查是否为移动设备
const checkMobile = () => {
  isMobile.value = window.innerWidth < 640; // sm breakpoint
};

// 监听窗口大小变化
onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkMobile);
});

const chartData = computed(() => ({
  labels: props.data.map((item) => item.label),
  datasets: [
    {
      data: props.data.map((item) => item.value),
      backgroundColor: colors,
      borderColor: "white",
      borderWidth: 2,
      borderRadius: 5,
      spacing: 2,
      hoverOffset: 4,
    },
  ],
}));

// 图表配置
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: "62%",
  layout: {
    padding: isMobile.value
      ? {
          left: 10,
          right: 10,
          top: 10,
          bottom: 10,
        }
      : {
          left: 0,
          right: 100,
          top: 10,
          bottom: 10,
        },
  },
  plugins: {
    legend: {
      position: isMobile.value ? "bottom" : ("right" as const),
      align: "center" as const,
      labels: {
        usePointStyle: true,
        pointStyle: "circle",
        padding: isMobile.value ? 15 : 20,
        boxWidth: 8,
        boxHeight: 8,
        font: {
          family: "'Source Sans Pro', 'Helvetica', 'Arial', sans-serif",
          size: 12,
          weight: "500",
        },
        color: "#6B7280",
        generateLabels: (chart) => {
          const datasets = chart.data.datasets;
          return chart.data.labels.map((label, index) => ({
            text: label,
            fillStyle: datasets[0].backgroundColor[index],
            strokeStyle: datasets[0].backgroundColor[index],
            hidden: false,
            index: index,
          }));
        },
      },
    },
    title: {
      display: !!props.title,
      text: props.title,
      align: isMobile.value ? "center" : ("start" as const),
      padding: {
        top: isMobile.value ? 5 : 10,
        bottom: isMobile.value ? 10 : 20,
      },
      font: {
        size: isMobile.value ? 14 : 16,
        weight: "bold",
        family: "'Source Sans Pro', 'Helvetica', 'Arial', sans-serif",
      },
      color: "#374151",
    },
    tooltip: {
      enabled: true,
      backgroundColor: "rgba(255, 255, 255, 0.9)",
      titleColor: "#374151",
      bodyColor: "#374151",
      borderColor: "rgba(0, 0, 0, 0.1)",
      borderWidth: 1,
      padding: 12,
      boxPadding: 6,
      usePointStyle: true,
      callbacks: {
        label: function (context) {
          const label = context.label || "";
          const value = context.raw || 0;
          const total = context.dataset.data.reduce(
            (a: number, b: number) => a + b,
            0
          );
          const percentage = (((value as number) / total) * 100).toFixed(1);
          return `${label}: ${value} (${percentage}%)`;
        },
      },
    },
  },
  elements: {
    arc: {
      borderWidth: 2,
    },
  },
}));

// 额外的插件配置
const plugins = [
  {
    id: "customCanvasBackgroundColor",
    beforeDraw: (chart) => {
      const ctx = chart.canvas.getContext("2d");
      if (ctx) {
        ctx.save();
        ctx.globalCompositeOperation = "destination-over";
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, chart.width, chart.height);
        ctx.restore();
      }
    },
  },
];
</script>

<style scoped>
.w-full {
  width: 100%;
}
.h-full {
  height: 100%;
}
</style>
