<!-- src/components/FolderSection.vue -->
<template>
  <div class="h-2/5 border-b">
    <!-- 顶部栏 -->
    <div class="flex justify-between items-center px-4 py-3 border-b">
      <h2 class="text-lg font-semibold">聊天和文件夹</h2>
      <div class="flex gap-2">
        <button
          @click="openCreateModal('folder')"
          class="p-1.5 rounded hover:bg-gray-100"
          title="创建新文件夹"
        >
          <Folder class="w-5 h-5 text-gray-600" />
        </button>
        <button
          @click="openCreateModal('chat')"
          class="p-1.5 rounded hover:bg-gray-100"
          title="创建新聊天"
        >
          <MessageSquarePlus class="w-5 h-5 text-gray-600" />
        </button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="overflow-y-auto h-[calc(100%-3.5rem)] p-2 space-y-1">
      <!-- 未分类聊天列表 -->
      <div
        class="mb-4"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDropToUnorganized($event)"
        :class="{
          'folder-drop-target': true,
          'drag-over': isDraggingOver && !draggingChat?.folder_id,
        }"
      >
        <div class="text-sm text-gray-500 mb-2">未分类聊天</div>
        <div
          v-for="chat in unorganizedChats"
          :key="chat.id"
          class="group relative flex items-center p-2 rounded hover:bg-gray-100"
          :class="{
            'selected-chat': selectedChat === chat.id,
          }"
          @click="selectChat(chat)"
          @dblclick="enableDragging(chat)"
          :draggable="isDraggable(chat)"
          @dragstart="handleDragStart($event, chat)"
          @dragend="handleDragEnd"
          @mouseleave="handleMouseLeave(chat)"
        >
          <div
            v-if="selectedChat === chat.id"
            class="absolute left-0 top-0 bottom-0 w-1 bg-blue-500 selection-indicator rounded-full"
          ></div>
          <MessageSquare class="w-4 h-4 text-gray-500 mr-2" />
          <span class="flex-1 truncate">{{ chat.name }}</span>
          <div class="hidden group-hover:flex items-center gap-1">
            <button
              @click.stop="editChat(chat)"
              class="p-1 rounded hover:bg-gray-200"
            >
              <Edit class="w-3.5 h-3.5 text-gray-500" />
            </button>
            <button
              @click.stop="deleteChat(chat.id)"
              class="p-1 rounded hover:bg-gray-200"
            >
              <Trash2 class="w-3.5 h-3.5 text-gray-500" />
            </button>
            <button
              @click.stop="openMoveToFolderModal(chat)"
              class="p-1 rounded hover:bg-gray-200"
            >
              <FolderInput class="w-3.5 h-3.5 text-gray-500" />
            </button>
          </div>
        </div>
      </div>

      <!-- 文件夹列表 -->
      <div
        v-for="folder in folders"
        :key="folder.id"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDropToFolder($event, folder.id)"
        :class="{
          'folder-drop-target': true,
          'drag-over': isDraggingOver && draggingChat?.folder_id !== folder.id,
        }"
      >
        <div
          class="group relative flex items-center p-2 rounded hover:bg-gray-100 cursor-pointer"
        >
          <ChevronRight
            class="w-4 h-4 text-gray-500 mr-1 transition-transform cursor-pointer"
            :class="{ 'rotate-90': expandedFolders.includes(folder.id) }"
            @click.stop="toggleFolder(folder.id)"
          />
          <Folder class="w-4 h-4 text-gray-500 mr-2" />
          <span class="flex-1 truncate" @click.stop="toggleFolder(folder.id)">{{
            folder.name
          }}</span>
          <div class="hidden group-hover:flex items-center gap-1">
            <button
              @click.stop="createChatInFolder(folder)"
              class="p-1 rounded hover:bg-gray-200"
              title="在文件夹中创建聊天"
            >
              <MessageSquarePlus class="w-3.5 h-3.5 text-gray-500" />
            </button>
            <button
              @click.stop="editFolder(folder)"
              class="p-1 rounded hover:bg-gray-200"
            >
              <Edit class="w-3.5 h-3.5 text-gray-500" />
            </button>
            <button
              @click.stop="deleteFolder(folder.id)"
              class="p-1 rounded hover:bg-gray-200"
            >
              <Trash2 class="w-3.5 h-3.5 text-gray-500" />
            </button>
          </div>
        </div>

        <!-- 文件夹内容区域 -->
        <div
          v-if="expandedFolders.includes(folder.id)"
          class="ml-6 space-y-1 mt-1"
        >
          <div
            v-for="chat in getFolderChats(folder.id)"
            :key="chat.id"
            class="group relative flex items-center p-2 rounded hover:bg-gray-100"
            :class="{
              'selected-chat': selectedChat === chat.id,
            }"
            @click="selectChat(chat)"
            @dblclick="enableDragging(chat)"
            :draggable="isDraggable(chat)"
            @dragstart="handleDragStart($event, chat)"
            @dragend="handleDragEnd"
            @mouseleave="handleMouseLeave(chat)"
          >
            <div
              v-if="selectedChat === chat.id"
              class="absolute left-0 top-0 bottom-0 w-1 bg-blue-500"
            ></div>
            <MessageSquare class="w-4 h-4 text-gray-500 mr-2" />
            <span class="flex-1 truncate">{{ chat.name }}</span>
            <div class="hidden group-hover:flex items-center gap-1">
              <button
                @click.stop="editChat(chat)"
                class="p-1 rounded hover:bg-gray-200"
              >
                <Edit class="w-3.5 h-3.5 text-gray-500" />
              </button>
              <button
                @click.stop="deleteChat(chat.id)"
                class="p-1 rounded hover:bg-gray-200"
              >
                <Trash2 class="w-3.5 h-3.5 text-gray-500" />
              </button>
              <button
                @click.stop="removeFromFolder(chat.id)"
                class="p-1 rounded hover:bg-gray-200"
              >
                <FolderMinus class="w-3.5 h-3.5 text-gray-500" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑模态框 -->
    <Dialog :open="showCreateModal" @close="closeModal">
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{{
            modalType === "folder"
              ? editingFolder
                ? "编辑文件夹"
                : "创建新文件夹"
              : editingChat
              ? "编辑聊天"
              : "创建新聊天"
          }}</DialogTitle>
        </DialogHeader>
        <div class="py-4">
          <input
            v-model="itemName"
            type="text"
            class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            :placeholder="
              modalType === 'folder' ? '输入文件夹名称' : '输入聊天名称'
            "
            @keyup.enter="saveItem"
          />

          <!-- 添加这部分 -->
          <div v-if="modalType === 'chat' && !editingChat">
            <div class="mt-3">
              <label class="block text-sm text-gray-600 mb-1"
                >选择文件夹（可选）</label
              >
              <select
                v-model="selectedFolderId"
                class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option :value="null">不放入文件夹</option>
                <option
                  v-for="folder in folders"
                  :key="folder.id"
                  :value="folder.id"
                >
                  {{ folder.name }}
                </option>
              </select>
            </div>

            <!-- 添加提示词选择器 -->
            <div class="mt-3">
              <label class="block text-sm text-gray-600 mb-1"
                >选择提示词（可选）</label
              >
              <PromptSelector v-model="selectedPrompt" />
            </div>
          </div>
        </div>
        <DialogFooter>
          <button
            @click="closeModal"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
          >
            取消
          </button>
          <button
            @click="saveItem"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ml-2"
          >
            {{ editingFolder || editingChat ? "保存" : "创建" }}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- 移动到文件夹模态框 -->
    <Dialog :open="showMoveModal" @close="closeMoveModal">
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>移动到文件夹</DialogTitle>
        </DialogHeader>
        <div class="py-4">
          <select
            v-model="selectedFolderId"
            class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option :value="null">不放入文件夹</option>
            <option
              v-for="folder in folders"
              :key="folder.id"
              :value="folder.id"
            >
              {{ folder.name }}
            </option>
          </select>
        </div>
        <DialogFooter>
          <button
            @click="closeMoveModal"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
          >
            取消
          </button>
          <button
            @click="moveToFolder"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ml-2"
          >
            移动
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useUserStore } from "@/stores/user";
import { request } from "@/utils/request";
import PromptSelector from "./PromptSelector.vue";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog/index.js";
import {
  Folder,
  MessageSquare,
  MessageSquarePlus,
  Edit,
  Trash2,
  FolderInput,
  FolderMinus,
  ChevronRight,
} from "lucide-vue-next";
import { ElMessage } from "element-plus";
// State
const userStore = useUserStore();
const folders = ref([]);
const chats = ref([]);
const showCreateModal = ref(false);
const showMoveModal = ref(false);
const modalType = ref("folder");
const itemName = ref("");
const editingFolder = ref(null);
const editingChat = ref(null);
const selectedFolderId = ref(null);
const movingChat = ref(null);
const expandedFolders = ref([]);
const draggingChat = ref(null);
const isDraggingOver = ref(false);
const selectedChat = ref(null);
const draggableChat = ref(null);
const selectedPrompt = ref(null);

const emit = defineEmits(["create-chat", "folder-change", "chat-change"]);

// API methods
const fetchChats = () => request("/api/chats");

const createChat = async (data) => {
  return request("/api/chats", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
};

const updateChat = async (chatId, data) => {
  return request(`/api/chats/${chatId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
};

const deleteChatRequest = async (chatId) => {
  return request(`/api/chats/${chatId}`, {
    method: "DELETE",
  });
};

const createFolder = async (name) => {
  return request("/api/folders", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });
};

const updateFolder = async (folderId, data) => {
  return request(`/api/folders/${folderId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
};

const handleDropToFolder = async (event, folderId) => {
  event.preventDefault();
  isDraggingOver.value = false;

  if (!draggingChat.value) return;

  try {
    await updateChat(draggingChat.value.id, { folder_id: folderId });
    // 重新获取最新的聊天列表
    const newChats = await fetchChats();
    chats.value = newChats;

    if (!expandedFolders.value.includes(folderId)) {
      expandedFolders.value.push(folderId);
    }
    emit("chat-change", chats.value);
  } catch (error) {
    console.error("移动聊天失败:", error);
  }
};

const handleDropToUnorganized = async (event) => {
  event.preventDefault();
  isDraggingOver.value = false;

  if (!draggingChat.value) return;

  const chat = draggingChat.value;
  if (!chat.folder_id) return;

  try {
    await updateChat(chat.id, { folder_id: null });
    // 重新获取最新的聊天列表
    const newChats = await fetchChats();
    chats.value = newChats;

    console.log("已移动到未分类");
    emit("chat-change", chats.value);
  } catch (error) {
    console.error("移动聊天失败:", error);
  }
};
const deleteFolder = async (folderId) => {
  if (!confirm("确定要删除此文件夹吗？")) return;

  try {
    await request(`/api/folders/${folderId}`, { method: "DELETE" });
    // 添加这行来更新本地数据
    folders.value = folders.value.filter((f) => f.id !== folderId);
    emit("folder-change", folders.value);
  } catch (error) {
    console.error("删除文件夹失败:", error);
  }
};

// Computed
const unorganizedChats = computed(() => {
  return chats.value.filter((chat) => !chat.folder_id);
});

const getFolderChats = (folderId) => {
  return chats.value.filter((chat) => chat.folder_id === folderId);
};

// Mounted
onMounted(async () => {
  try {
    const [chatsData, foldersData] = await Promise.all([
      fetchChats(),
      request("/api/folders"),
    ]);
    chats.value = chatsData;
    folders.value = foldersData;
  } catch (error) {
    console.error("Error fetching data:", error);
  }
});

// 添加事件处理方法
const handleDragOver = (event) => {
  event.preventDefault();
  isDraggingOver.value = true;
};

const handleDragLeave = () => {
  isDraggingOver.value = false;
};
// Methods
const handleMouseLeave = (chat) => {
  if (draggableChat.value === chat.id) {
    draggableChat.value = null;
  }
};

const selectChat = (chat) => {
  selectedChat.value = selectedChat.value === chat.id ? null : chat.id;
  emit("chat-selected", chat);
};

const enableDragging = (chat) => {
  if (selectedChat.value !== chat.id) {
    selectedChat.value = chat.id;
  }
  draggableChat.value = chat.id;
};

const isDraggable = (chat) => {
  return draggableChat.value === chat.id;
};

const toggleFolder = (folderId) => {
  const index = expandedFolders.value.indexOf(folderId);
  if (index === -1) {
    expandedFolders.value.push(folderId);
  } else {
    expandedFolders.value.splice(index, 1);
  }
};

const openCreateModal = (type) => {
  modalType.value = type;
  editingFolder.value = null;
  editingChat.value = null;
  itemName.value = "";
  selectedFolderId.value = null;
  showCreateModal.value = true;
};

const closeModal = () => {
  showCreateModal.value = false;
  editingFolder.value = null;
  editingChat.value = null;
  itemName.value = "";
  selectedFolderId.value = null;
  selectedPrompt.value = null; // 添加这行
};

const editFolder = (folder) => {
  modalType.value = "folder";
  editingFolder.value = folder;
  itemName.value = folder.name;
  showCreateModal.value = true;
};

const editChat = (chat) => {
  modalType.value = "chat";
  editingChat.value = chat;
  itemName.value = chat.name;
  showCreateModal.value = true;
};

const deleteChat = async (chatId) => {
  if (!confirm("确定要删除这个聊天吗？")) return;

  try {
    await deleteChatRequest(chatId);
    chats.value = chats.value.filter((c) => c.id !== chatId);

    if (selectedChat.value === chatId) {
      selectedChat.value = null;
      draggableChat.value = null;
    }

    console.log("聊天删除成功");
    emit("chat-change", chats.value);
  } catch (error) {
    console.error("删除聊天失败:", error);
  }
};

const handleDragStart = (event, chat) => {
  if (!isDraggable(chat)) {
    event.preventDefault();
    return;
  }
  draggingChat.value = chat;
  event.dataTransfer.effectAllowed = "move";
  event.target.classList.add("opacity-50");
};

const handleDragEnd = (event) => {
  draggingChat.value = null;
  draggableChat.value = null;
  isDraggingOver.value = false;
  event.target.classList.remove("opacity-50");
};

// const handleDropToUnorganized = async (event) => {
//   event.preventDefault();
//   isDraggingOver.value = false;

//   if (!draggingChat.value) return;

//   const chat = draggingChat.value;
//   if (!chat.folder_id) return;

//   try {
//     await updateChat(chat.id, { folder_id: null });
//     const chatIndex = chats.value.findIndex((c) => c.id === chat.id);
//     if (chatIndex !== -1) {
//       chats.value[chatIndex].folder_id = null;
//     }
//     console.log("已移动到未分类");
//     emit("chat-change", chats.value);
//   } catch (error) {
//     console.error("移动聊天失败:", error);
//   }
// };

const openMoveToFolderModal = (chat) => {
  movingChat.value = chat;
  selectedFolderId.value = chat.folder_id;
  showMoveModal.value = true;
};

const closeMoveModal = () => {
  showMoveModal.value = false;
  movingChat.value = null;
  selectedFolderId.value = null;
};

const moveToFolder = async () => {
  if (!movingChat.value) return;

  try {
    const updatedChat = await updateChat(movingChat.value.id, {
      folder_id: selectedFolderId.value,
    });

    const chatIndex = chats.value.findIndex((c) => c.id === updatedChat.id);
    if (chatIndex !== -1) {
      chats.value[chatIndex] = updatedChat;
    }

    console.log("移动成功");
    emit("chat-change", chats.value);
    closeMoveModal();
  } catch (error) {
    console.error("移动聊天失败:", error);
  }
};

const removeFromFolder = async (chatId) => {
  try {
    const updatedChat = await updateChat(chatId, { folder_id: null });
    const chatIndex = chats.value.findIndex((c) => c.id === chatId);
    if (chatIndex !== -1) {
      chats.value[chatIndex] = updatedChat;
    }
    emit("chat-change", chats.value);
  } catch (error) {
    console.error("从文件夹移除失败:", error);
  }
};

const createChatInFolder = (folder) => {
  modalType.value = "chat";
  editingChat.value = null;
  itemName.value = "";
  selectedFolderId.value = folder.id;
  showCreateModal.value = true;
};

const saveItem = async () => {
  if (!itemName.value.trim()) return;

  try {
    if (modalType.value === "chat") {
      if (editingChat.value) {
        // 编辑现有聊天
        const updatedChat = await updateChat(editingChat.value.id, {
          name: itemName.value,
        });
        const index = chats.value.findIndex(
          (c) => c.id === editingChat.value.id
        );
        if (index !== -1) {
          chats.value[index] = updatedChat;
        }
        emit("chat-change", chats.value);
        ElMessage.success({
          message: "聊天更新成功",
          plain: true,
        });
      } else {
        // 创建新聊天
        let newChat;
        const chatData = {
          name: itemName.value,
          folder_id: selectedFolderId.value,
        };

        if (selectedPrompt.value) {
          // 使用提示词创建聊天
          try {
            const response = await request(
              `/api/chats/with-prompt/${selectedPrompt.value.type}/${selectedPrompt.value.id}`,
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify(chatData),
              }
            );

            // 使用返回的chat_id构造chat对象
            newChat = {
              id: response.chat_id,
              name: itemName.value,
              folder_id: selectedFolderId.value,
              created_at: new Date().toISOString(),
            };
            ElMessage.success({
              message: "提示词聊天创建成功",
              plain: true,
            });
          } catch (error) {
            // 获取错误响应的具体内容
            const errorJson = await error.response.json();
            ElMessage.error({
              message: errorJson.detail || "创建聊天失败，请重试",
              plain: true,
            });
            return;
          }
        } else {
          // 普通创建聊天
          try {
            newChat = await createChat(chatData);
            ElMessage.success({
              message: "聊天创建成功",
              plain: true,
            });
          } catch (error) {
            const errorJson = await error.response.json();
            ElMessage.error({
              message: errorJson.detail || "创建聊天失败，请重试",
              plain: true,
            });
            return;
          }
        }

        // 添加新聊天到列表
        chats.value.push(newChat);
        emit("create-chat", newChat);
        emit("chat-change", chats.value);

        // 如果在文件夹中创建,确保文件夹是展开的
        if (
          selectedFolderId.value &&
          !expandedFolders.value.includes(selectedFolderId.value)
        ) {
          expandedFolders.value.push(selectedFolderId.value);
        }
      }
    } else if (modalType.value === "folder") {
      if (editingFolder.value) {
        // 编辑现有文件夹
        const updatedFolder = await updateFolder(editingFolder.value.id, {
          name: itemName.value,
        });
        const index = folders.value.findIndex(
          (f) => f.id === editingFolder.value.id
        );
        if (index !== -1) {
          folders.value[index] = updatedFolder;
        }
        ElMessage.success({
          message: "文件夹更新成功",
          plain: true,
        });
      } else {
        // 创建新文件夹
        const newFolder = await createFolder(itemName.value);
        folders.value.push(newFolder);
        ElMessage.success({
          message: "文件夹创建成功",
          plain: true,
        });
      }
      emit("folder-change", folders.value);
    }

    closeModal();
  } catch (error) {
    console.error("保存失败:", error);
    // 处理最外层的错误
    try {
      const errorJson = await error.response.json();
      ElMessage.error({
        message: errorJson.detail || "操作失败，请重试",
        plain: true,
      });
    } catch {
      ElMessage.error({
        message: "操作失败，请重试",
        plain: true,
      });
    }
  }
};
</script>

<style scoped>
.selection-indicator {
  animation: indicatorAppear 0.3s ease-out;
  transform-origin: left;
}

@keyframes indicatorAppear {
  0% {
    transform: scaleX(0);
  }
  100% {
    transform: scaleX(1);
  }
}

.selected-chat {
  background-color: rgb(243 244 246);
}

.dragging {
  opacity: 0.5;
}

[draggable="true"] {
  cursor: grab;
}

[draggable="false"] {
  cursor: pointer;
}

.folder-drop-target {
  border: 2px dashed transparent;
  transition: border-color 0.2s;
}

.folder-drop-target.drag-over {
  border-color: #4299e1;
}
</style>
