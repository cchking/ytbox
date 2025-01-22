// stores/user.js
import { defineStore } from "pinia";

export const useUserStore = defineStore("user", {
  state: () => ({
    token: null,
    id: null,
    username: null,
    email: null,
    role: null,
    isActive: null,
    vipUntil: null,
    createdAt: null,
  }),

  actions: {
    setUserInfo(data) {
      this.token = data.access_token;
      this.id = data.id;
      this.username = data.username;
      this.email = data.email;
      this.role = data.role;
      this.isActive = data.is_active;
      this.vipUntil = data.vip_until;
      this.createdAt = data.created_at;

      // 同时保存到 localStorage
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("userId", data.id);
      localStorage.setItem("username", data.username);
      localStorage.setItem("userEmail", data.email);
      localStorage.setItem("userRole", data.role);
      localStorage.setItem("isActive", data.is_active);
      localStorage.setItem("vipUntil", data.vip_until);
      localStorage.setItem("createdAt", data.created_at);
    },

    clearUserInfo() {
      // 清除所有用户信息
      this.$reset();
      localStorage.clear();
    },
  },

  getters: {
    isAdmin: (state) => state.role === "admin",
    isAuthenticated: (state) => !!state.token,
  },
});
