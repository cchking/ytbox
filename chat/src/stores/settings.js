// src/stores/settings.js
import { defineStore } from "pinia";

export const useSettingsStore = defineStore("settings", {
  state: () => ({
    title: "加载中...",
    logo: null,
    vip_benefits: null,
    user_guide: null,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchSettings() {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetch("/api/frontend-settings");
        const data = await response.json();

        // 更新状态
        this.title = data.title;
        this.logo = data.logo;
        this.vip_benefits = data.vip_benefits;
        this.user_guide = data.user_guide;

        // 更新文档标题
        if (data.title) {
          document.title = data.title;
        }

        // 更新网站图标
        if (data.logo) {
          const favicon = document.querySelector('link[rel="icon"]');
          if (favicon) {
            favicon.href = data.logo;
          } else {
            const newFavicon = document.createElement("link");
            newFavicon.rel = "icon";
            newFavicon.href = data.logo;
            document.head.appendChild(newFavicon);
          }
        }
      } catch (error) {
        this.error = error.message || "未知错误";
      } finally {
        this.loading = false;
      }
    },
  },
});
