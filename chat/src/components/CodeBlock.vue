// CodeBlock.vue
<template>
  <div class="relative bg-[#1a1b26] rounded-lg overflow-hidden group">
    <!-- 顶部栏 -->
    <div class="h-8 bg-[#1f2937] flex items-center px-4">
      <div class="flex gap-1.5">
        <!-- 折叠按钮 -->
        <button
          class="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors flex items-center justify-center"
          @click="isCollapsed = !isCollapsed"
          :title="isCollapsed ? '展开代码' : '折叠代码'"
        >
          <span class="hidden group-hover:inline-flex text-[10px] text-red-100">
            {{ isCollapsed ? "+" : "-" }}
          </span>
        </button>

        <!-- 最小化按钮 -->
        <button
          class="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors flex items-center justify-center"
          @click="isMinimized = !isMinimized"
          :title="isMinimized ? '展开完整代码' : '收起部分代码'"
        >
          <span
            class="hidden group-hover:inline-flex text-[10px] text-yellow-100"
          >
            {{ isMinimized ? "↓" : "↑" }}
          </span>
        </button>

        <!-- 复制按钮 -->
        <button
          class="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors flex items-center justify-center"
          @click="handleCopy"
          title="复制代码"
        >
          <span
            class="hidden group-hover:inline-flex text-[10px] text-green-100"
          >
            {{ isCopied ? "✓" : "⎘" }}
          </span>
        </button>
      </div>

      <div class="flex items-center ml-4">
        <span class="text-gray-400 text-sm select-none">{{
          validLanguage
        }}</span>
        <span
          class="text-xs text-green-400 ml-2 transition-opacity"
          :class="{ 'opacity-0': !isCopied, 'opacity-100': isCopied }"
        >
          已复制!
        </span>
      </div>
    </div>

    <!-- 折叠状态 -->
    <template v-if="isCollapsed">
      <div
        class="p-2 text-sm text-gray-400 cursor-pointer hover:bg-[#2d2d2d] transition-colors text-center"
        @click="isCollapsed = false"
      >
        [已折叠的代码块] 点击展开
      </div>
    </template>

    <!-- 代码内容 -->
    <template v-else>
      <div class="p-4 font-mono text-sm">
        <pre class="!bg-transparent overflow-auto">
          <code 
            :class="'hljs language-' + validLanguage"
            v-html="processedCode"
          ></code>
        </pre>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { ElMessage } from "element-plus";
import hljs from "highlight.js";

const props = defineProps({
  code: {
    type: String,
    required: true,
  },
  language: {
    type: String,
    default: "plaintext",
  },
});

const isCollapsed = ref(false);
const isMinimized = ref(false);
const isCopied = ref(false);

// 确保使用有效的语言
const validLanguage = computed(() => {
  return hljs.getLanguage(props.language) ? props.language : "plaintext";
});

// 处理代码高亮和最小化
const processedCode = computed(() => {
  try {
    const codeToProcess = isMinimized.value
      ? props.code.split("\n").slice(0, 3).join("\n") + "\n..."
      : props.code;

    return hljs.highlight(codeToProcess, {
      language: validLanguage.value,
    }).value;
  } catch (err) {
    console.error("高亮处理错误:", err);
    return props.code;
  }
});

// 复制功能
const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.code);
    isCopied.value = true;
    ElMessage({
      message: "复制成功",
      type: "success",
      duration: 1500,
    });
    setTimeout(() => {
      isCopied.value = false;
    }, 1500);
  } catch (err) {
    console.error("复制失败:", err);
    ElMessage({
      message: "复制失败",
      type: "error",
      duration: 1500,
    });
  }
};
</script>

<style>
.hljs {
  background: transparent !important;
}

/* 语法高亮颜色 */
.hljs-keyword {
  color: #ff7b72;
}
.hljs-function {
  color: #d2a8ff;
}
.hljs-string {
  color: #a5d6ff;
}
.hljs-number {
  color: #79c0ff;
}
.hljs-title {
  color: #d2a8ff;
}
.hljs-params {
  color: #ffa657;
}
.hljs-comment {
  color: #8b949e;
  font-style: italic;
}
.hljs-doctag {
  color: #ff7b72;
}
.hljs-meta {
  color: #79c0ff;
}
.hljs-variable {
  color: #ffa657;
}
.hljs-type {
  color: #ff7b72;
}
.hljs-attr {
  color: #79c0ff;
}
.hljs-built_in {
  color: #ffa657;
}
.hljs-name {
  color: #7ee787;
}
.hljs-selector-tag {
  color: #ff7b72;
}
.hljs-constant {
  color: #79c0ff;
}
.hljs-class {
  color: #ff7b72;
}
.hljs-tag {
  color: #7ee787;
}
.hljs-subst {
  color: #e6edf3;
}
.hljs-regexp {
  color: #a5d6ff;
}
.hljs-symbol {
  color: #79c0ff;
}
.hljs-bullet {
  color: #79c0ff;
}
.hljs-link {
  color: #79c0ff;
}
.hljs-operator {
  color: #79c0ff;
}
</style>
