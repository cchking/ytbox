<!-- src/views/user/main.vue -->
<template>
  <div class="flex h-screen bg-white overflow-hidden">
    <!-- 移动端菜单按钮 -->
    <button
      v-if="isMobile"
      class="fixed left-4 top-4 z-50 p-2 rounded-lg hover:bg-gray-100"
      @click="openSidebar"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>

    <!-- 遮罩层 -->
    <div
      v-if="isMobile && sidebarVisible"
      class="fixed inset-0 bg-black bg-opacity-50 z-10"
      @click="closeSidebar"
    ></div>

    <!-- 侧边栏 -->
    <Sidebar
      ref="sidebarRef"
      :username="username"
      :userType="userType"
      :themeColors="themeColors"
      :initialWidth="320"
      :is-mobile="isMobile"
      :is-visible="!isMobile || sidebarVisible"
      @themeChange="changeTheme"
      @widthChange="handleSidebarWidthChange"
      @chat-selected="handleChatSelect"
      @create-chat="handleCreateChat"
      @chat-change="handleChatsChange"
      class="z-20"
    />

    <!-- 主要内容区域 -->
    <div
      class="flex-1 h-full transition-all duration-300"
      :style="{
        marginLeft: isMobile ? '0' : `${sidebarWidth}px`,
        width: isMobile ? '100%' : `calc(100% - ${sidebarWidth}px)`,
      }"
    >
      <!-- 头部 -->
      <ChatHeader
        :currentModel="currentModel"
        :models="models"
        :sidebarWidth="isMobile ? 0 : sidebarWidth"
        :is-mobile="isMobile"
        @select="selectModel"
        @toggle-sidebar="openSidebar"
      />

      <div class="h-full pt-16 flex flex-col">
        <!-- 消息列表区域 -->
        <template v-if="currentChat">
          <MessageList
            :messages="messages"
            :current-model="currentModel"
            :models="models"
            :is-thinking="false"
            :isMobile="isMobile"
            :sidebarWidth="sidebarWidth"
            @edit-message="handleEditMessage"
            @regenerate="handleRegenerate"
          />

          <!-- 输入区域 -->
          <MessageInput
            v-model="newMessage"
            :file-previews="filePreviews"
            :isThinking="isThinking"
            :isGenerating="isGenerating"
            :isMobile="isMobile"
            :sidebarWidth="sidebarWidth"
            :chat-id="currentChat?.id"
            @send="sendMessage"
            @stop="stopGeneration"
            @fileSelect="handleFileSelect"
            @paste="handlePaste"
            @drop="handleDrop"
            @removeFile="handleRemoveFile"
          />
        </template>

        <!-- 未选择聊天时的提示 -->
        <div
          v-else
          class="flex-1 flex items-center justify-center text-gray-500"
        >
          选择或创建一个聊天开始对话
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect, onMounted, onUnmounted } from "vue";
import { request } from "@/utils/request";
import ChatHeader from "../../components/ChatHeader.vue";
import Sidebar from "../../components/Sidebar.vue";
import MessageList from "../../components/MessageList.vue";
import MessageInput from "../../components/MessageInput.vue";

// State
const sidebarWidth = ref(320);
const username = ref("用户名");
const userType = ref("高级用户");
const newMessage = ref("");
const messages = ref([]);
const filePreviews = ref([]);
const currentChat = ref(null);
const isThinking = ref(false);
const currentModel = ref(null); // 改为响应式引用
const models = ref([]); // 改为响应式数组
// 添加侧边栏显示状态
const sidebarVisible = ref(false);
const isMobile = ref(false);
const sidebarRef = ref(null);
const controller = ref(null); // 用于控制请求的 AbortController
const isGenerating = ref(false); // 用于跟踪是否正在生成响应
// 检查是否为移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768;
  // 如果切换到移动端，自动关闭侧边栏
  if (isMobile.value) {
    sidebarVisible.value = false;
  }
};

// main.vue 中修改这些方法
const openSidebar = () => {
  console.log("Opening sidebar"); // 添加调试日志
  if (sidebarRef.value) {
    sidebarRef.value.open();
  }
};

const closeSidebar = () => {
  console.log("Closing sidebar"); // 添加调试日志
  if (sidebarRef.value) {
    sidebarRef.value.close();
  }
};

// 添加停止生成的函数
const stopGeneration = () => {
  console.log("停止生成"); // 调试日志
  if (controller.value) {
    controller.value.abort();
    controller.value = null;
  }
  // 设置最后一条消息的状态
  const lastMessage = messages.value[messages.value.length - 1];
  if (lastMessage) {
    lastMessage.pending = false;
    lastMessage.content;
  }
  isThinking.value = false;
  isGenerating.value = false;
};

// 获取Token
const getToken = () => {
  const token = localStorage.getItem("token");
  if (!token) {
    console.error("No token found");
    return null;
  }
  return token;
};

// Methods
const handleSidebarWidthChange = (width) => {
  sidebarWidth.value = width;
};

const selectModel = (model) => {
  currentModel.value = model;
  localStorage.setItem("selectedModel", JSON.stringify(model));
  console.log("Selected model:", model);
};

// 初始化时加载保存的模型
const initializeModel = () => {
  const savedModel = localStorage.getItem("selectedModel");
  if (savedModel) {
    try {
      currentModel.value = JSON.parse(savedModel);
    } catch (error) {
      console.error("Error parsing saved model:", error);
    }
  }
};

const changeTheme = (color) => {
  document.documentElement.setAttribute("data-theme", color);
};

// 处理文件相关
const handleFileSelect = async (files) => {
  const token = getToken();
  if (!token) return;

  try {
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append("files", file);
    });

    const response = await request("/api/upload", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    filePreviews.value = [
      ...filePreviews.value,
      ...response.files.map((file) => ({
        id: file.id,
        name: file.name,
        url: file.url,
        type: file.type,
      })),
    ];
  } catch (error) {
    console.error("文件上传失败:", error);
    if (error.status === 401) {
      localStorage.removeItem("token");
    }
  }
};

const handleEditMessage = async (messageId, editData) => {
  isThinking.value = true;
  try {
    const response = await fetch(
      `/api/chats/${currentChat.value.id}/messages/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`,
          Accept: "text/event-stream",
        },
        body: JSON.stringify(editData),
      }
    );

    // 处理401错误
    if (response.status === 401) {
      router.push("/login");
      return;
    }

    // 处理其他错误状态
    if (!response.ok) {
      const errorText = await response.text();
      const lastMessage = messages.value[messages.value.length - 1];
      if (lastMessage) {
        lastMessage.content = "```json\n" + errorText + "\n```";
        lastMessage.pending = false;
        lastMessage.error = true;
      }
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();

      // 如果读取完成，确保设置 pending 为 false
      if (done) {
        const lastMessage = messages.value[messages.value.length - 1];
        if (lastMessage) {
          lastMessage.pending = false;
        }
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.trim() === "") continue;
        if (line.trim() === "data: [DONE]") {
          // 收到 [DONE] 时也设置 pending 为 false
          const lastMessage = messages.value[messages.value.length - 1];
          if (lastMessage) {
            lastMessage.pending = false;
          }
          continue;
        }

        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.choices && data.choices[0]) {
              const { delta } = data.choices[0];
              const lastMessage = messages.value[messages.value.length - 1];

              if (delta.role) {
                lastMessage.role = delta.role;
              }

              if (delta.content) {
                lastMessage.content += delta.content;
              }

              // 如果收到结束标志，设置 pending 为 false
              if (data.choices[0].finish_reason === "stop") {
                lastMessage.pending = false;
              }
            }
          } catch (e) {
            console.error("Error parsing SSE data:", e);
            continue;
          }
        }
      }
    }
  } catch (error) {
    console.error("编辑消息失败:", error);
    const lastMessage = messages.value[messages.value.length - 1];
    if (lastMessage) {
      lastMessage.content = "```json\n" + error.toString() + "\n```";
      lastMessage.pending = false;
      lastMessage.error = true;
    }
  } finally {
    isThinking.value = false;
  }
};

const handleRegenerate = async (messageId) => {
  isThinking.value = true;
  let retryCount = 0;
  const maxRetries = 3;
  const attemptRegenerate = async () => {
    try {
      console.log("[Debug] Starting regenerate message:", messageId);
      console.log("[Debug] Current messages:", messages.value);

      // 找到当前消息的索引
      const messageIndex = messages.value.findIndex(
        (msg) => msg.id === messageId
      );
      if (messageIndex === -1) {
        throw new Error("Cannot find message to regenerate");
      }

      // 如果是最后一条消息，保留前一条用户消息
      if (messageIndex === messages.value.length - 1 && messageIndex > 0) {
        messages.value.splice(messageIndex);
      } else {
        // 如果不是最后一条消息，删除当前消息及其后续所有消息
        messages.value.splice(messageIndex);
      }

      // 添加一个新的 pending 消息
      const newMessage = {
        role: "assistant",
        content: "",
        pending: true,
        model_name: currentModel.value.name,
        model_icon: currentModel.value.icon,
      };
      messages.value.push(newMessage);

      // 构建请求体
      const requestBody = {
        model: currentModel.value.name,
        content: "",
        regenerate_message_id: messageId,
      };

      console.log("[Debug] Request payload:", requestBody);
      console.log("[Debug] Chat ID:", currentChat.value.id);

      const response = await fetch(
        `/api/chats/${currentChat.value.id}/messages/stream`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getToken()}`,
            Accept: "text/event-stream",
          },
          body: JSON.stringify(requestBody),
        }
      );

      // 处理401错误
      if (response.status === 401) {
        router.push("/login");
        return;
      }

      // 处理其他错误状态
      if (!response.ok) {
        const errorText = await response.text();
        const lastMessage = messages.value[messages.value.length - 1];
        lastMessage.content = "```json\n" + errorText + "\n```";
        lastMessage.pending = false;
        lastMessage.error = true;
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          const lastMessage = messages.value[messages.value.length - 1];
          if (lastMessage) {
            lastMessage.pending = false;
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.trim() === "") continue;
          if (line.trim() === "data: [DONE]") {
            const lastMessage = messages.value[messages.value.length - 1];
            if (lastMessage) {
              lastMessage.pending = false;
            }
            continue;
          }

          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.choices && data.choices[0]) {
                const { delta } = data.choices[0];
                const lastMessage = messages.value[messages.value.length - 1];

                if (delta.role) {
                  lastMessage.role = delta.role;
                }

                if (delta.content) {
                  lastMessage.content += delta.content;
                }

                if (data.choices[0].finish_reason === "stop") {
                  lastMessage.pending = false;
                }
              }
            } catch (e) {
              console.error("[Error] Error parsing SSE data:", e);
              continue;
            }
          }
        }
      }
    } catch (error) {
      console.error("[Error] In regenerate attempt:", error);
      retryCount++;
      if (retryCount < maxRetries) {
        console.log(
          `[Debug] Retrying regenerate message (${retryCount}/${maxRetries})...`
        );
        await new Promise((resolve) => setTimeout(resolve, 1000 * retryCount));
        return attemptRegenerate();
      }
      // 显示错误消息为代码块
      const lastMessage = messages.value[messages.value.length - 1];
      if (lastMessage) {
        lastMessage.content = "```json\n" + error.toString() + "\n```";
        lastMessage.pending = false;
        lastMessage.error = true;
      }
      throw error;
    }
  };

  try {
    await attemptRegenerate();
  } catch (error) {
    console.error("[Error] Failed to regenerate message:", error);
    messages.value.push({
      role: "system",
      content: `重新生成消息失败: ${error.message}`,
      error: true,
    });
    const lastMessage = messages.value[messages.value.length - 1];
    if (lastMessage) {
      lastMessage.pending = false;
    }
  } finally {
    isThinking.value = false;
  }
};
const handlePaste = async (event) => {
  const items = (event.clipboardData || event.originalEvent.clipboardData)
    .items;
  const files = [];

  for (const item of items) {
    if (item.kind === "file") {
      const file = item.getAsFile();
      if (file) files.push(file);
    }
  }

  if (files.length > 0) {
    await handleFileSelect(files);
  }
};

const handleDrop = async (event) => {
  const files = [...event.dataTransfer.files];
  if (files.length > 0) {
    await handleFileSelect(files);
  }
};

const handleRemoveFile = (fileId) => {
  const index = filePreviews.value.findIndex((f) => f.id === fileId);
  if (index !== -1) {
    filePreviews.value.splice(index, 1);
  }
};

// 聊天相关
const handleChatSelect = async (chat) => {
  const token = getToken();
  if (!token) return;

  currentChat.value = chat;
  if (chat) {
    try {
      const response = await request(`/api/chats/${chat.id}/messages`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      messages.value = response.map((msg) => ({
        ...msg,
        pending: false,
      }));
    } catch (error) {
      console.error("获取消息失败:", error);
      if (error.status === 401) {
        localStorage.removeItem("token");
      }
    }
  } else {
    messages.value = [];
  }
  if (isMobile.value) {
    closeSidebar();
  }
};

const handleChatCreate = (chat) => {
  currentChat.value = chat;
  messages.value = [];
};

const handleChatsChange = (chats) => {
  if (!chats.find((c) => c.id === currentChat.value?.id)) {
    currentChat.value = null;
    messages.value = [];
  }
};

// 发送消息
const sendMessage = async () => {
  if (
    !currentChat.value ||
    (!newMessage.value.trim() && filePreviews.value.length === 0)
  ) {
    return;
  }

  const token = getToken();
  if (!token) return;

  // 确保已选择模型
  if (!currentModel.value) {
    messages.value.push({
      id: Date.now(),
      role: "system",
      content: "请先选择一个AI模型",
      error: true,
    });
    return;
  }

  isThinking.value = true;
  isGenerating.value = true;
  controller.value = new AbortController();
  const messageContent = newMessage.value;

  // 区分图片和其他文件
  const imageFiles = filePreviews.value.filter((file) =>
    file.type.startsWith("image/")
  );
  const otherFiles = filePreviews.value.filter(
    (file) => !file.type.startsWith("image/")
  );

  try {
    // 构建用户消息内容
    let messageArray = [];

    // 添加文本内容
    if (messageContent.trim()) {
      messageArray.push({
        type: "text",
        text: messageContent.trim(),
      });
    }

    // 添加图片
    if (imageFiles.length > 0) {
      messageArray.push(
        ...imageFiles.map((file) => ({
          type: "image_url",
          image_url: {
            url: file.url,
          },
        }))
      );
    }

    // 添加其他文件
    if (otherFiles.length > 0) {
      messageArray.push(
        ...otherFiles.map((file) => ({
          type: "file",
          file_url: {
            url: file.url,
          },
        }))
      );
    }

    // 添加用户消息到列表
    const userMessage = {
      role: "user",
      content: JSON.stringify(messageArray),
      pending: false,
    };

    messages.value.push(userMessage);

    // 清空输入和文件
    newMessage.value = "";
    filePreviews.value = [];

    // 添加AI思考中的消息
    const aiMessage = {
      role: "assistant",
      content: "",
      pending: true,
      model_name: currentModel.value.name,
      model_icon: currentModel.value.icon,
    };
    messages.value.push(aiMessage);

    // 构建请求体
    const requestBody = {
      content: messageContent,
      model: currentModel.value.name,
    };

    // 处理图片
    if (imageFiles.length > 0) {
      requestBody.images = imageFiles.map((file) => ({
        url: file.url,
        detail: "auto",
      }));
    }

    // 处理其他文件，需要按照后端要求的格式构造
    if (otherFiles.length > 0) {
      requestBody.files = otherFiles.map((file) => ({
        type: "file",
        file_url: {
          url: file.url,
        },
      }));
    }

    const response = await fetch(
      `/api/chats/${currentChat.value.id}/messages/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          Accept: "text/event-stream",
        },
        body: JSON.stringify(requestBody),
        signal: controller.value.signal,
      }
    );

    // 处理401错误
    if (response.status === 401) {
      router.push("/login");
      return;
    }

    // 处理其他错误状态
    if (!response.ok) {
      const errorText = await response.text();
      const lastMessage = messages.value[messages.value.length - 1];
      lastMessage.content = "```json\n" + errorText + "\n```";
      lastMessage.pending = false;
      lastMessage.error = true;
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    const lastMessage = messages.value[messages.value.length - 1];

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          if (lastMessage) {
            lastMessage.pending = false;
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.trim() === "") continue;
          if (line.trim() === "data: [DONE]") continue;

          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.choices && data.choices[0]) {
                const { delta } = data.choices[0];

                if (delta.role) {
                  lastMessage.role = delta.role;
                }

                if (delta.content) {
                  lastMessage.content += delta.content;
                }

                if (data.choices[0].finish_reason === "stop") {
                  lastMessage.pending = false;
                }
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e);
              continue;
            }
          }
        }
      }
    } catch (error) {
      if (error.name === "AbortError") {
        console.log("Request was aborted");
        if (lastMessage) {
          lastMessage.content;
          lastMessage.pending = false;
        }
      } else {
        console.error("Stream reading error:", error);
        if (lastMessage) {
          lastMessage.content = "```json\n" + error.toString() + "\n```";
          lastMessage.error = true;
          lastMessage.pending = false;
        }
      }
    }
  } catch (error) {
    if (error.name === "AbortError") {
      console.log("Request was aborted");
      const lastMessage = messages.value[messages.value.length - 1];
      if (lastMessage) {
        lastMessage.content;
        lastMessage.pending = false;
      }
    } else {
      console.error("发送消息失败:", error);
      const lastMessage = messages.value[messages.value.length - 1];
      if (
        lastMessage &&
        lastMessage.role === "assistant" &&
        lastMessage.pending
      ) {
        lastMessage.content = "```json\n" + error.toString() + "\n```";
        lastMessage.pending = false;
        lastMessage.error = true;
      }
    }
  } finally {
    isThinking.value = false;
    isGenerating.value = false;
    controller.value = null;
  }
};

// 生命周期钩子
onMounted(() => {
  checkMobile();
  // 添加窗口大小变化监听
  window.addEventListener("resize", checkMobile);
  const token = getToken();
  if (!token) {
    console.error("No token found");
    return;
  }
  initializeModel(); // 初始化模型选择
});
onUnmounted(() => {
  window.removeEventListener("resize", checkMobile);
  // ... 其他原有的 onUnmounted 代码
});
// 清理函数
const cleanup = () => {
  messages.value = [];
  filePreviews.value = [];
  newMessage.value = "";
  isThinking.value = false;
};
</script>

<style scoped>
.message-list {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-track {
  background: transparent;
}

.message-list::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}
</style>
