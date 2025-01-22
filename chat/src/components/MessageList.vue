<!-- MessageList.vue -->
<template>
  <div
    class="fixed inset-0"
    :style="{ left: isMobile ? '0' : `${sidebarWidth}px` }"
  >
    <!-- 顶部模型选择器 -->
    <div
      class="fixed top-0 right-0 h-16 bg-white shadow-md z-10 transition-all duration-200"
      :style="{ left: isMobile ? '0' : `${sidebarWidth}px` }"
    >
      <ModelSelector
        :current-model="currentModel"
        :models="models"
        @select="$emit('select', $event)"
      />
    </div>

    <!-- 消息容器 -->
    <div
      ref="messageContainer"
      class="w-full h-full overflow-y-auto pb-32"
      :style="{ paddingTop: '64px' }"
    >
      <div class="w-full p-4 space-y-4">
        <!-- 消息列表 -->
        <div
          v-for="(message, index) in messages"
          :key="message.id"
          class="message-container"
        >
          <!-- 用户消息部分 -->
          <div
            v-if="message.role === 'user'"
            class="flex justify-end mb-4 mr-[5%]"
          >
            <div
              class="bg-white rounded-lg px-4 py-3 max-w-[80%] shadow-[0_4px_12px_-4px_rgba(0,0,0,0.2)]"
            >
              <div
                class="items-start grid grid-cols-[minmax(0,1fr),auto] gap-3"
              >
                <!-- 消息内容区域 -->
                <div class="space-y-2 w-full">
                  <!-- 编辑状态 -->
                  <div v-if="message.isEditing" class="space-y-2">
                    <textarea
                      v-model="message.editContent"
                      class="w-full p-2 border rounded-lg resize-none"
                      rows="3"
                    ></textarea>
                    <div class="flex justify-end gap-2">
                      <button
                        @click="cancelEdit(message)"
                        class="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
                      >
                        取消
                      </button>
                      <button
                        @click="saveEdit(message)"
                        class="px-3 py-1 text-sm text-white bg-blue-500 hover:bg-blue-600 rounded-lg"
                      >
                        重新发送
                      </button>
                    </div>
                  </div>

                  <!-- 非编辑状态 -->
                  <div v-else>
                    <!-- 历史消息内容 - 处理JSON格式的消息 -->
                    <div
                      v-if="parseMessageContent(message.content)"
                      class="space-y-3 w-full"
                    >
                      <div class="flex flex-col gap-3">
                        <!-- 首先显示文本内容 -->
                        <template
                          v-for="(item, index) in parseMessageContent(
                            message.content
                          )"
                          :key="index"
                        >
                          <div
                            v-if="item.type === 'text'"
                            class="relative group cursor-pointer"
                            @click="
                              !isNextMessagePending(index) && startEdit(message)
                            "
                          >
                            <div
                              class="whitespace-pre-wrap break-words transition-colors"
                              :class="{
                                'opacity-50': isNextMessagePending(index),
                              }"
                            >
                              {{ item.text }}
                            </div>
                          </div>
                        </template>

                        <!-- 然后显示图片内容 -->
                        <template
                          v-for="(item, index) in parseMessageContent(
                            message.content
                          )"
                          :key="index"
                        >
                          <div
                            v-if="item.type === 'image_url'"
                            class="relative group w-full"
                          >
                            <img
                              :src="item.image_url.url"
                              class="max-w-full h-auto object-contain rounded-lg cursor-pointer hover:opacity-95 transition-opacity bg-gray-50"
                              @click="openPreview(item.image_url.url)"
                              alt="上传的图片"
                            />
                          </div>
                        </template>

                        <!-- 文件内容 -->
                        <template
                          v-for="(item, index) in parseMessageContent(
                            message.content
                          )"
                          :key="index"
                        >
                          <div
                            v-if="item.type === 'file'"
                            class="relative group w-full max-w-full overflow-hidden"
                          >
                            <div
                              class="flex flex-col sm:flex-row items-start sm:items-center gap-2 p-2.5 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
                            >
                              <div class="flex-shrink-0">
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  width="18"
                                  height="18"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  stroke-width="2"
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                  class="text-gray-500"
                                >
                                  <path
                                    d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                                  ></path>
                                  <polyline points="14 2 14 8 20 8"></polyline>
                                </svg>
                              </div>
                              <div class="min-w-0 w-full flex-1">
                                <div class="flex flex-col">
                                  <div
                                    class="text-sm font-medium text-gray-900 truncate"
                                  >
                                    {{ item.file_url.url.split("/").pop() }}
                                  </div>
                                  <div
                                    class="text-xs text-gray-500 truncate"
                                    :title="item.file_url.url"
                                  >
                                    {{ item.file_url.url }}
                                  </div>
                                </div>
                              </div>
                              <a
                                :href="item.file_url.url"
                                target="_blank"
                                class="flex-shrink-0 p-1.5 text-gray-700 hover:bg-white rounded-lg border border-gray-200 transition-colors self-start sm:self-center ml-auto sm:ml-0"
                                title="下载文件"
                              >
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  width="14"
                                  height="14"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  stroke-width="2"
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                >
                                  <path
                                    d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"
                                  ></path>
                                  <polyline
                                    points="7 10 12 15 17 10"
                                  ></polyline>
                                  <line x1="12" y1="15" x2="12" y2="3"></line>
                                </svg>
                              </a>
                            </div>
                          </div>
                        </template>
                      </div>
                    </div>

                    <!-- 新发送的消息内容 -->
                    <div v-else class="space-y-3">
                      <!-- 文本内容 -->
                      <div
                        v-if="message.content"
                        class="relative group cursor-pointer"
                        @click="
                          !isNextMessagePending(index) && startEdit(message)
                        "
                      >
                        <div
                          class="whitespace-pre-wrap break-words transition-colors"
                          :class="{ 'opacity-50': isNextMessagePending(index) }"
                        >
                          {{ message.content }}
                        </div>
                      </div>

                      <!-- 图片内容 -->
                      <div
                        v-if="message.images && message.images.length"
                        class="space-y-2"
                      >
                        <div
                          v-for="(image, imageIndex) in message.images"
                          :key="imageIndex"
                          class="relative group w-full"
                        >
                          <img
                            :src="image.url"
                            class="max-w-full h-auto object-contain rounded-lg cursor-pointer hover:opacity-95 transition-opacity bg-gray-50"
                            @click="openPreview(image.url)"
                            alt="上传的图片"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 用户头像和编辑按钮区域 -->
                <div
                  class="relative w-8 h-8 rounded-full flex-shrink-0 self-start group/avatar cursor-pointer"
                  @click="!isNextMessagePending(index) && startEdit(message)"
                >
                  <!-- 默认头像显示 -->
                  <div
                    class="w-full h-full bg-indigo-500 text-white flex items-center justify-center text-sm font-medium rounded-full group-hover/avatar:opacity-0"
                    :class="{ 'opacity-50': isNextMessagePending(index) }"
                  >
                    {{ getUserInitial() }}
                  </div>
                  <!-- 编辑图标 -->
                  <div
                    class="absolute inset-0 opacity-0 group-hover/avatar:opacity-100 flex items-center justify-center bg-gray-100 rounded-full transition-opacity"
                    :class="{
                      'cursor-not-allowed': isNextMessagePending(index),
                    }"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      :class="{
                        'text-gray-400': isNextMessagePending(index),
                        'text-gray-600': !isNextMessagePending(index),
                      }"
                    >
                      <path
                        d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                      />
                      <path
                        d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- AI助手消息 -->
          <div
            v-else-if="message.role === 'assistant'"
            class="flex justify-start mb-4 ml-[5%]"
          >
            <!-- AI头像 -->
            <div class="flex-shrink-0 mr-3">
              <div class="w-8 h-8 relative">
                <img
                  v-if="getModelIcon(message)"
                  :src="getModelIcon(message)"
                  class="w-full h-full object-cover rounded"
                  :alt="message.model_name"
                  @error="handleImageError"
                />
                <div
                  v-else
                  class="w-full h-full flex items-center justify-center bg-gray-200 rounded text-sm"
                >
                  {{ message.model_name?.charAt(0) || "?" }}
                </div>
              </div>
            </div>

            <!-- 消息内容 -->
            <div
              :class="[
                'rounded-lg px-4 py-2 max-w-[80%] shadow-[0_4px_12px_-4px_rgba(0,0,0,0.2)] markdown-body relative group',
                message.error ? 'bg-red-50' : 'bg-white',
              ]"
            >
              <!-- 操作按钮组 -->
              <div
                class="absolute right-2 bottom-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
              >
                <!-- 复制按钮 -->
                <button
                  v-if="!message.pending"
                  @click="copyMessage(message.content)"
                  class="p-1.5 rounded-md hover:bg-gray-100 transition-all duration-200"
                  title="复制内容"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="text-gray-500"
                  >
                    <rect
                      x="9"
                      y="9"
                      width="13"
                      height="13"
                      rx="2"
                      ry="2"
                    ></rect>
                    <path
                      d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                    ></path>
                  </svg>
                </button>

                <!-- 重新回答按钮 -->
                <button
                  v-if="!message.pending"
                  @click="$emit('regenerate', message.id)"
                  class="p-1.5 rounded-md hover:bg-gray-100 transition-all duration-200"
                  title="重新回答"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="text-gray-500"
                  >
                    <path
                      d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"
                    />
                    <path d="M3 3v5h5" />
                    <path
                      d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"
                    />
                    <path d="M16 16h5v5" />
                  </svg>
                </button>
              </div>

              <!-- 消息内容 -->
              <div
                v-if="message.content === '' && message.pending"
                class="typing-cursor-container min-h-[24px]"
              >
                <LoadingDots />
              </div>
              <div
                v-else-if="message.pending"
                class="whitespace-pre-wrap break-words"
              >
                <RealTimeMarkdown
                  :content="message.content"
                  :is-pending="message.pending"
                />
              </div>
              <div
                v-else
                class="whitespace-pre-wrap break-words"
                v-html="renderMarkdown(message.content)"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <slot name="input"></slot>
  </div>
  <el-dialog
    v-model="previewVisible"
    :show-close="true"
    :modal="true"
    width="auto"
    class="preview-dialog"
    destroy-on-close
    @close="closePreview"
  >
    <div class="flex items-center justify-center">
      <img
        :src="previewImageUrl"
        class="max-w-full max-h-[80vh] object-contain rounded-lg"
        @wheel.prevent="handleImageZoom"
        @mousedown="startDrag"
        @mousemove="onDrag"
        @mouseup="stopDrag"
        @mouseleave="stopDrag"
        :style="imageStyle"
        alt="预览图片"
      />
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted, h, computed } from "vue";
import { ElMessage } from "element-plus";
import "element-plus/dist/index.css";
import ModelSelector from "./ModelSelector.vue";
import { marked } from "marked";
import hljs from "highlight.js";
import katex from "katex";
import "highlight.js/styles/github.css";
import "katex/dist/katex.css";
import LoadingDots from "./LoadingDots.vue";

// 定义 emit 事件
const emit = defineEmits(["select", "edit-message", "regenerate"]);

// 组件 props 定义
const props = defineProps({
  messages: { type: Array, required: true },
  sidebarWidth: { type: Number, default: 320 },
  currentModel: { type: Object, required: true },
  models: { type: Array, required: true },
  isMobile: { type: Boolean, default: false },
});

// 消息容器引用
const messageContainer = ref(null);

// 添加缩放和拖动相关的状态
const previewVisible = ref(false);
const previewImageUrl = ref("");
const scale = ref(1);
const position = ref({ x: 0, y: 0 });
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });
const userScrolling = ref(false);

// 计算图片样式
const imageStyle = computed(() => ({
  transform: `scale(${scale.value}) translate(${position.value.x}px, ${position.value.y}px)`,
  cursor: isDragging.value ? "grabbing" : "grab",
  transition: isDragging.value ? "none" : "transform 0.3s",
}));

// 处理图片缩放
const handleImageZoom = (event) => {
  event.preventDefault();
  const delta = event.deltaY > 0 ? 0.9 : 1.1;
  const newScale = scale.value * delta;
  if (newScale >= 0.5 && newScale <= 3) {
    scale.value = newScale;
  }
};

// 开始拖动
const startDrag = (event) => {
  isDragging.value = true;
  dragStart.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y,
  };
};

// 拖动中
const onDrag = (event) => {
  if (isDragging.value) {
    position.value = {
      x: event.clientX - dragStart.value.x,
      y: event.clientY - dragStart.value.y,
    };
  }
};

// 停止拖动
const stopDrag = () => {
  isDragging.value = false;
};

// 修改预览对话框中的图片部分
const resetPreview = () => {
  scale.value = 1;
  position.value = { x: 0, y: 0 };
};

// 修改 openPreview 函数
const openPreview = (url) => {
  previewImageUrl.value = url;
  previewVisible.value = true;
  resetPreview();
};

// 获取模型图标
const getModelIcon = (message) => {
  if (message.model_icon) {
    return message.model_icon;
  }
  if (message.model_name === props.currentModel?.name) {
    return props.currentModel?.icon;
  }
  const model = props.models.find((m) => m.name === message.model_name);
  return model?.icon;
};

// 检查下一条消息是否待处理
const isNextMessagePending = (index) => {
  const messages = props.messages;
  if (index === messages.length - 1) return false;
  return messages[index + 1]?.pending || false;
};

// 复制消息内容
const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content);
    ElMessage({
      message: "复制成功",
      type: "success",
      duration: 2000,
      plain: true,
    });
  } catch (err) {
    console.error("复制消息失败:", err);
    ElMessage({
      message: "复制失败",
      type: "error",
      duration: 2000,
      plain: true,
    });
  }
};

const parseMessageContent = (content) => {
  try {
    // 处理直接的图片数组情况
    if (typeof content === "string" && !content.startsWith("[")) {
      return null;
    }

    // 如果已经是数组则直接返回
    if (Array.isArray(content)) {
      return content;
    }

    // 尝试解析 JSON 字符串
    const parsedContent = JSON.parse(content);
    if (Array.isArray(parsedContent)) {
      return parsedContent;
    }

    return null;
  } catch (error) {
    console.error("解析消息内容失败:", error);
    return null;
  }
};

// 编辑相关的函数也需要相应修改
const startEdit = (message) => {
  message.isEditing = true;
  // 如果是数组格式的消息，只编辑文本部分
  const parsedContent = parseMessageContent(message.content);
  if (parsedContent) {
    const textParts = parsedContent
      .filter((item) => item.type === "text")
      .map((item) => item.text)
      .join("\n");
    message.editContent = textParts;
  } else {
    message.editContent = message.content;
  }
};

const saveEdit = async (message) => {
  if (!message.editContent?.trim()) return;

  const currentIndex = props.messages.findIndex((m) => m.id === message.id);
  if (currentIndex === -1) return;

  const editedContent = message.editContent;

  // 处理消息内容的更新
  const parsedContent = parseMessageContent(message.content);
  let newContent;

  if (parsedContent) {
    // 如果原消息是数组格式，保留图片，更新文本
    newContent = parsedContent.map((item) => {
      if (item.type === "text") {
        return { type: "text", text: editedContent };
      }
      return item;
    });
    // 转换为字符串
    newContent = JSON.stringify(newContent);
  } else {
    newContent = editedContent;
  }

  // 更新消息内容
  message.content = newContent;
  message.isEditing = false;
  message.editContent = null;

  // 删除后续消息
  if (currentIndex < props.messages.length - 1) {
    props.messages.splice(currentIndex + 1);
  }

  // 添加新的AI回复
  props.messages.push({
    role: "assistant",
    content: "",
    pending: true,
    model_name: props.currentModel.name,
    model_icon: props.currentModel.icon,
  });

  // 触发编辑事件
  emit("edit-message", message.id, {
    content: newContent,
    model: props.currentModel.name,
    edit_message_id: message.id,
  });
};
// 取消编辑
const cancelEdit = (message) => {
  message.isEditing = false;
  message.editContent = null;
};

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.style.display = "none";
  event.target.nextElementSibling.style.display = "flex";
};

// 配置代码高亮
hljs.configure({
  ignoreUnescapedHTML: true,
  throwUnescapedHTML: false,
});

// 自定义代码块渲染

// 配置 marked 渲染器
const renderer = new marked.Renderer();

renderer.code = (code, language) => {
  let finalCode = code;
  let finalLang = language || "plaintext";

  // 处理代码内容
  if (typeof code === "object") {
    try {
      if (code.raw && code.text) {
        finalCode = code.text.trim();
        finalLang = code.lang || finalLang;
      } else {
        finalCode = JSON.stringify(code, null, 2);
        finalLang = "json";
      }
    } catch (e) {
      finalCode = String(code);
    }
  }

  try {
    const validLanguage = hljs.getLanguage(finalLang) ? finalLang : "plaintext";
    const highlighted = hljs.highlight(finalCode, {
      language: validLanguage,
    }).value;

    // 生成唯一ID
    const blockId = Math.random().toString(36).substring(2);

    return `<pre class="code-block" data-block-id="${blockId}">
    <div class="code-block-header">
      <div class="flex gap-1.5 control-buttons">
        <button class="control-btn bg-red-500 hover:bg-red-600"
          onclick="toggleCollapse('${blockId}')"
          title="折叠代码块">
        </button>
        <button class="control-btn bg-yellow-500 hover:bg-yellow-600"
          onclick="toggleMinimize('${blockId}')"
          title="最小化代码">
        </button>
        <button class="control-btn bg-green-500 hover:bg-green-600"
          onclick="copyCode(this)"
          data-code="${encodeURIComponent(finalCode)}"
          title="复制代码">
        </button>
      </div>
      <span class="code-language">${validLanguage}</span>
    </div>
    <code class="hljs language-${validLanguage}">${highlighted}</code>
  </pre>`;
  } catch (error) {
    console.error("代码高亮错误:", error);
    return `<pre><code class="hljs">${finalCode}</code></pre>`;
  }
};

// 配置 marked 选项
marked.setOptions({
  renderer,
  highlight: null, // 使用 CodeBlock 组件处理高亮
  gfm: true,
  breaks: true,
  headerIds: false,
  mangle: false,
});

// 实时 Markdown 组件
const RealTimeMarkdown = {
  props: {
    content: {
      type: String,
      required: true,
    },
    isPending: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const renderedContent = ref("");

    // 监听内容变化
    watch(
      () => props.content,
      (newContent) => {
        if (!newContent) {
          renderedContent.value = "";
          return;
        }

        // 处理实时内容
        renderedContent.value = processCodeBlock(newContent);

        // 如果是待处理状态，添加打字机光标
        if (props.isPending) {
          renderedContent.value += '<span class="typing-cursor"></span>';
        }
      },
      { immediate: true }
    );

    // 处理代码块
    const processCodeBlock = (text) => {
      const codeBlockRegex = /```(\w+)?\n([\s\S]+?)```/g;
      let lastIndex = 0;
      let result = "";

      for (const match of text.matchAll(codeBlockRegex)) {
        const [fullMatch, lang, code] = match;
        const start = match.index;

        // 添加代码块前的文本
        result += marked(text.slice(lastIndex, start));

        // 渲染代码块
        try {
          const language = lang || "plaintext";
          const highlighted = hljs.highlight(code.trim(), {
            language: hljs.getLanguage(language) ? language : "plaintext",
          }).value;

          result += `<pre class="code-block"><div class="code-block-header">
            <span class="code-language">${language}</span>
          </div><code class="hljs language-${language}">${highlighted}</code></pre>`;
        } catch (e) {
          result += `<pre><code>${code}</code></pre>`;
        }

        lastIndex = start + fullMatch.length;
      }

      // 添加剩余文本
      result += marked(text.slice(lastIndex));
      return result;
    };

    return () =>
      h("div", {
        innerHTML: renderedContent.value,
        class: "real-time-markdown",
      });
  },
};

// 配置 Marked
marked.setOptions({
  renderer,
  highlight: function (code, lang) {
    let finalCode = code;
    let language = lang;

    if (typeof code === "object") {
      try {
        if (code.raw && code.text) {
          finalCode = code.text.trim();
          language = code.lang || language;
        } else {
          finalCode = JSON.stringify(code, null, 2);
          language = "json";
        }
      } catch (e) {
        finalCode = String(code);
      }
    }

    try {
      if (language && hljs.getLanguage(language)) {
        return hljs.highlight(finalCode, { language }).value;
      }
      return hljs.highlightAuto(finalCode).value;
    } catch (e) {
      console.error("高亮错误:", e);
      return finalCode;
    }
  },
  gfm: true,
  breaks: true,
  langPrefix: "hljs language-",
  headerIds: false,
  mangle: false,
});

// 数学公式渲染
const renderMath = (content, displayMode = false) => {
  try {
    return katex.renderToString(content, {
      displayMode,
      throwOnError: false,
      strict: false,
    });
  } catch (e) {
    console.error("KaTeX 错误:", e);
    return content;
  }
};

// 处理数学公式
const processMath = (text) => {
  if (typeof text !== "string") {
    text = String(text || "");
  }
  text = text.replace(/\$([^\$\n]+?)\$/g, (_, p1) => renderMath(p1, false));
  text = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, p1) => renderMath(p1, true));
  return text;
};

// Markdown 渲染
const renderMarkdown = (content) => {
  if (!content) return "";

  try {
    if (typeof content === "object" && content.type === "code") {
      return marked(
        content.raw ||
          `\`\`\`${content.lang || ""}\n${content.text || ""}\n\`\`\``
      );
    }

    const contentStr = String(content);
    let rendered = marked(contentStr);
    rendered = processMath(rendered);
    return rendered;
  } catch (err) {
    console.error("Markdown 渲染错误:", err);
    return String(content);
  }
};

// 获取用户名首字母
const getUserInitial = () => {
  const username = localStorage.getItem("username");
  return username ? username.charAt(0).toUpperCase() : "U";
};

// 判断是否在底部附近
const isNearBottom = () => {
  if (!messageContainer.value) return false;
  const container = messageContainer.value;
  // 认为距离底部 100px 以内就算是在底部
  return (
    container.scrollHeight - container.scrollTop - container.clientHeight < 100
  );
};

// 监听滚动事件
const handleScroll = () => {
  if (!messageContainer.value) return;

  const container = messageContainer.value;
  const atBottom =
    container.scrollHeight - container.scrollTop - container.clientHeight < 100;

  // 如果用户向上滚动，标记为正在查看历史
  if (!atBottom) {
    userScrolling.value = true;
  }

  // 如果用户滚动到底部，重置标记
  if (atBottom) {
    userScrolling.value = false;
  }
};

// 滚动到底部
const scrollToBottom = async (smooth = true) => {
  await nextTick();
  if (!messageContainer.value) return;

  // 只在以下情况滚动到底部：
  // 1. 用户不在查看历史消息
  // 2. 是用户发送的新消息
  // 3. AI 回复完成
  if (!userScrolling.value || smooth) {
    messageContainer.value.scrollTo({
      top: messageContainer.value.scrollHeight,
      behavior: smooth ? "smooth" : "auto",
    });
  }
};

// 监听消息变化
watch(
  () => props.messages,
  (messages, oldMessages) => {
    const lastMessage = messages[messages.length - 1];
    const isNewUserMessage =
      lastMessage?.role === "user" && messages.length > oldMessages.length;
    const isCompletedAIMessage =
      lastMessage?.role === "assistant" && !lastMessage.pending;

    // 只在这些情况下滚动到底部：
    // 1. 用户发送新消息
    // 2. AI 回复完成
    if (isNewUserMessage || isCompletedAIMessage) {
      userScrolling.value = false; // 重置用户滚动状态
      scrollToBottom(true);
    }
  },
  { deep: true }
);

// 在组件挂载时添加滚动监听
onMounted(() => {
  messageContainer.value?.addEventListener("scroll", handleScroll);
  scrollToBottom(false);
});

// 在组件卸载时清理
onUnmounted(() => {
  messageContainer.value?.removeEventListener("scroll", handleScroll);
});

// 处理窗口大小变化
const handleResize = () => scrollToBottom(false);

// 监听消息变化
watch(
  () => props.messages,
  (messages) => {
    // 检查最后一条消息是否是待处理状态
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && !lastMessage.pending) {
      // 完整回复时强制滚动到底部
      scrollToBottom(true);
    } else {
      // 流式回复时只在用户在底部时滚动
      scrollToBottom(false);
    }
  },
  { deep: true }
);
// 折叠代码块
window.toggleCollapse = (blockId) => {
  const block = document.querySelector(`[data-block-id="${blockId}"]`);
  const code = block.querySelector("code");

  if (!block.hasAttribute("data-collapsed")) {
    block.setAttribute("data-collapsed", "true");
    // 设置为header的高度（2rem = 32px）
    block.style.height = "32px"; // 或者使用 "2rem"
    code.style.display = "none";
  } else {
    block.removeAttribute("data-collapsed");
    block.style.height = "auto";
    code.style.display = "block";
  }
};

// 最小化代码
window.toggleMinimize = (blockId) => {
  const block = document.querySelector(`[data-block-id="${blockId}"]`);
  const code = block.querySelector("code");

  if (!block.hasAttribute("data-minimized")) {
    block.setAttribute("data-minimized", "true");
    if (!code.hasAttribute("data-full")) {
      code.setAttribute("data-full", code.innerHTML);
    }
    const lines = code.textContent.split("\n");
    code.innerHTML = hljs.highlight(lines.slice(0, 3).join("\n") + "\n...", {
      language: code.className.replace("hljs language-", ""),
    }).value;
  } else {
    block.removeAttribute("data-minimized");
    code.innerHTML = code.getAttribute("data-full");
  }
};

// 复制代码功能
window.copyCode = async (button) => {
  try {
    const code = decodeURIComponent(button.getAttribute("data-code"));
    await navigator.clipboard.writeText(code);

    // 设置成功状态
    const span = button.querySelector("span");
    if (span) {
      span.textContent = "✓";
      button.style.backgroundColor = "#22c55e";

      setTimeout(() => {
        span.textContent = "⎘";
        button.style.backgroundColor = "";
      }, 1500);
    }

    ElMessage({
      message: "复制成功",
      type: "success",
      plain: true,
      duration: 1500,
    });
  } catch (err) {
    console.error("复制失败:", err);
    ElMessage({
      message: "复制失败",
      type: "error",
      plain: true,
      duration: 1500,
    });
  }
};

// 组件生命周期钩子
onMounted(() => {
  scrollToBottom(false);
  window.addEventListener("resize", handleResize);
  window.copyCode = copyCode;
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
});
</script>

<style>
/* 基础 Markdown 样式 */
.markdown-body.markdown-body {
  font-size: 1rem;
  line-height: 1.6;
  color: rgb(55, 65, 81);
}

/* 段落间距 */
.markdown-body.markdown-body p {
  margin: 0 0 8px 0;
  padding: 0;
}

/* 行内代码样式 */
.markdown-body.markdown-body code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier,
    monospace;
  font-size: 0.875em;
  color: #374151;
  background-color: rgba(0, 0, 0, 0.04);
  border-radius: 4px;
  padding: 0.2em 0.4em;
  margin: 0;
}

/* 代码块容器样式 */
.markdown-body.markdown-body pre {
  background-color: #111827; /* gray-900 */
  border-radius: 0.5rem;
  margin: 8px 0;
  padding: 0;
  position: relative;
  font-size: 13px;
  line-height: 1.45;
  overflow: hidden;
  padding-bottom: 0; /* 移除底部内边距 */
}

/* 代码块文本样式 */
.markdown-body.markdown-body pre code {
  display: block;
  padding: 1rem 1rem 1rem;
  margin: 0;
  font-size: 0.875rem;
  color: #d1d5db; /* gray-300 */
  word-break: normal;
  white-space: pre;
  border: 0;
  overflow-x: auto;
  background: transparent;
  tab-size: 2;
  line-height: 1.5;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  margin-bottom: 0; /* 移除底部外边距 */
  padding-bottom: 0.5rem; /* 控制底部内边距 */
}

/* 代码块头部样式 */
.code-block-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2rem;
  padding: 0 1rem;
  background-color: #1f2937; /* gray-800 */
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 1;
}

/* 控制按钮容器 */
.control-buttons {
  display: flex;
  gap: 0.375rem;
  margin-right: auto;
}

/* 控制按钮基础样式 */
.control-btn {
  width: 0.75rem;
  height: 0.75rem;
  border: none;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

/* 按钮文字样式 */
.control-btn span {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
  opacity: 0;
  transition: opacity 0.2s;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 鼠标悬停时显示文字 */
.control-btn:hover span {
  opacity: 1;
}

/* 语言标识样式 */
.code-language {
  color: #9ca3af; /* gray-400 */
  font-size: 0.75rem; /* text-xs */
  font-weight: 500;
  text-transform: lowercase;
  margin-left: auto;
}

/* 语法高亮颜色 */
.hljs-keyword,
.hljs-selector-tag,
.hljs-literal,
.hljs-section,
.hljs-link {
  color: #c084fc; /* purple-400 */
}

.hljs-string,
.hljs-doctag,
.hljs-regexp,
.hljs-template-tag {
  color: #86efac; /* green-300 */
}

.hljs-title,
.hljs-name,
.hljs-type {
  color: #93c5fd; /* blue-300 */
}

.hljs-attribute,
.hljs-number,
.hljs-addition {
  color: #fcd34d; /* yellow-300 */
}

.hljs-comment,
.hljs-quote,
.hljs-meta {
  color: #6b7280; /* gray-500 */
  font-style: italic;
}

.hljs-variable,
.hljs-template-variable {
  color: #fb7185; /* rose-400 */
}

.hljs-built_in,
.hljs-builtin-name {
  color: #67e8f9; /* cyan-300 */
}

/* 滚动条样式 */
.markdown-body.markdown-body pre code::-webkit-scrollbar {
  height: 0.375rem;
}

.markdown-body.markdown-body pre code::-webkit-scrollbar-thumb {
  background: #4b5563; /* gray-600 */
  border-radius: 0.25rem;
}

.markdown-body.markdown-body pre code::-webkit-scrollbar-track {
  background: transparent;
}

/* Markdown 标题样式 */
.markdown-body.markdown-body h1,
.markdown-body.markdown-body h2,
.markdown-body.markdown-body h3,
.markdown-body.markdown-body h4,
.markdown-body.markdown-body h5,
.markdown-body.markdown-body h6 {
  margin: 16px 0 8px 0;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body.markdown-body h1 {
  font-size: 1.5rem;
}
.markdown-body.markdown-body h2 {
  font-size: 1.25rem;
}
.markdown-body.markdown-body h3 {
  font-size: 1.125rem;
}
.markdown-body.markdown-body h4 {
  font-size: 1rem;
}
.markdown-body.markdown-body h5 {
  font-size: 0.875rem;
}
.markdown-body.markdown-body h6 {
  font-size: 0.85rem;
}

/* Markdown 列表样式 */
.markdown-body.markdown-body ul,
.markdown-body.markdown-body ol {
  margin: 4px 0;
  padding-left: 20px;
}

.markdown-body.markdown-body li + li {
  margin-top: 4px;
}

/* 引用样式 */
.markdown-body.markdown-body blockquote {
  margin: 8px 0;
  padding: 4px 12px;
  color: #656d76;
  border-left: 0.25em solid #d0d7de;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .markdown-body.markdown-body pre {
    border-radius: 0.375rem;
  }

  .code-block-header {
    height: 1.75rem;
  }

  .markdown-body.markdown-body pre code {
    font-size: 0.8125rem;
    margin-bottom: 0; /* 移除底部外边距 */
    padding-bottom: 0.5rem; /* 控制底部内边距 */
  }

  .control-btn {
    width: 0.625rem;
    height: 0.625rem;
  }

  .code-language {
    font-size: 0.625rem;
  }
}

/* 折叠和最小化状态 */
.markdown-body.markdown-body pre[data-collapsed="true"] {
  height: 2rem;
}

.markdown-body.markdown-body pre[data-collapsed="true"] code {
  display: none;
}

.markdown-body.markdown-body pre[data-minimized="true"] code {
  max-height: 6rem;
  overflow: hidden;
}

/* 打字机光标样式 */
.typing-cursor-container {
  display: flex;
  align-items: center;
  min-height: 24px;
  padding: 1px 0;
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1.2em;
  background-color: currentColor;
  margin-left: 1px;
  animation: blink 1s infinite;
  vertical-align: middle;
  position: relative;
  top: -1px;
}

@keyframes blink {
  0%,
  100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

/* 复制按钮状态 */
.copy-button.copied {
  background-color: #22c55e !important; /* green-500 */
}

.copy-button.copied span {
  opacity: 1;
  color: white;
}
/* 移动端优化样式 */
@media (max-width: 768px) {
  /* 代码块容器样式优化 */
  .markdown-body.markdown-body pre {
    border-radius: 0.5rem;
    margin: 12px 0; /* 增加外边距 */
  }

  /* 代码块头部样式优化 */
  .code-block-header {
    height: 2.5rem; /* 增加头部高度 */
    padding: 0 0.75rem;
  }

  /* 控制按钮样式优化 */
  .control-btn {
    width: 1rem; /* 增加按钮大小 */
    height: 1rem;
    min-width: 1rem; /* 确保最小尺寸 */
    min-height: 1rem;
  }

  /* 代码文本样式优化 */
  .markdown-body.markdown-body pre code {
    padding: 1rem 0.75rem 0.75rem; /* 增加顶部padding以适应更高的header */
    font-size: 0.9375rem; /* 增大字体 */
    line-height: 1.6; /* 增加行高 */
  }

  /* 语言标识样式优化 */
  .code-language {
    font-size: 0.8125rem; /* 增大字体 */
  }

  /* 控制按钮组间距优化 */
  .control-buttons {
    gap: 0.5rem; /* 增加按钮间距 */
  }

  /* 按钮文字样式优化 */
  .control-btn span {
    font-size: 12px; /* 增大图标字体 */
  }
}

/* 代码块折叠状态优化 */
@media (max-width: 768px) {
  .markdown-body.markdown-body pre[data-collapsed="true"] {
    height: 2.5rem !important; /* 与header高度匹配 */
  }

  /* 滚动条样式优化 */
  .markdown-body.markdown-body pre code::-webkit-scrollbar {
    height: 0.5rem; /* 增大滚动条尺寸 */
  }

  /* 触摸区域优化 */
  .control-btn {
    position: relative;
    touch-action: manipulation; /* 优化触摸操作 */
  }

  /* 增加按钮点击区域 */
  .control-btn::after {
    content: "";
    position: absolute;
    top: -8px;
    right: -8px;
    bottom: -8px;
    left: -8px;
  }
}
</style>
