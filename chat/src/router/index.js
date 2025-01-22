import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/user";
const routes = [
  {
    path: "/",
    name: "Root",
    component: () => import("../views/LogIn.vue"),
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/LogIn.vue"),
  },
  {
    path: "/auth/linuxdo/callback",
    name: "LinuxDOCallback",
    component: () => import("../views/LinuxDOCallback.vue"),
  },
  {
    path: "/auth/github/callback",
    name: "GithubCallback",
    component: () => import("../views/GithubCallback.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("../views/Register.vue"),
  },
  {
    path: "/forgot-password",
    name: "ForgotPassword",
    component: () => import("../views/ForgotPassword.vue"),
  },
  {
    path: "/chat",
    name: "UserMain",
    component: () => import("../views/user/main.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/research",
    name: "Research",
    component: () => import("../views/user/research/main.vue"),
    meta: { requiresAuth: true },
  },
  // {
  //   path: "/market",
  //   component: () => import("../views/user/market/Market.vue"),
  //   meta: { requiresAuth: true },
  // },
  {
    path: "/console",
    name: "Console",
    component: () => import("../views/user/console/main.vue"),
    meta: { requiresAuth: true },
  },
  // {
  //   path: "/private-prompts",
  //   name: "PrivatePrompts",
  //   component: () => import("../views/user/console/PrivatePrompts.vue"),
  //   meta: { requiresAuth: true },
  // },
  // {
  //   path: "/coins-logs",
  //   name: "CoinsLogs",
  //   component: () => import("../views/user/console/CoinsLogs.vue"),
  //   meta: { requiresAuth: true },
  // },
  {
    path: "/purchase",
    name: "Purchase",
    component: () => import("../views/user/card/purchase.vue"),
    meta: { title: "卡密购买" },
  },
  {
    path: "/admin",
    component: () => import("../views/admin/layout/AdminLayout.vue"),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: "",
        redirect: "/admin/users",
      },
      {
        path: "users",
        name: "UserManagement",
        component: () => import("../views/admin/users/UserList.vue"),
        meta: { title: "用户管理" },
      },
      {
        path: "models",
        name: "ModelManagement",
        component: () => import("../views/admin/models/ModelList.vue"),
        meta: { title: "模型管理" },
      },
      {
        path: "channels",
        name: "ChannelManagement",
        component: () => import("../views/admin/channels/ChannelList.vue"),
        meta: { title: "渠道管理" },
      },
      {
        path: "/admin/logs",
        name: "Logs",
        component: () => import("../views/admin/logs/LogsView.vue"),
        meta: { title: "系统日志" },
      },
      {
        path: "/admin/ai-logs",
        component: () => import("../views/admin/logs/AilogsView.vue"),
        meta: { title: "AI日志" },
      },
      {
        path: "/admin/prompts",
        name: "Prompts",
        component: () => import("../views/admin/prompts/market.vue"),
        meta: { title: "提示词市场" },
      },
      {
        path: "/admin/marketmodels",
        name: "MarketModelsReview",
        component: () =>
          import("../views/admin/modelmarket/MarketModelsReview.vue"),
        meta: { title: "提示词市场" },
      },
      {
        path: "/admin/danger-logs",
        name: "DangerLogs",
        component: () => import("../views/admin/logs/DangerView.vue"),
        meta: { title: "违禁词日志" },
      },
      {
        path: "/admin/create-card",
        name: "Card",
        component: () => import("../views/admin/card/CreateViews.vue"),
        meta: { title: "卡密生成" },
      },
      {
        path: "/admin/settings",
        name: "settings",
        component: () =>
          import("../views/admin/settings/SettingManagement.vue"),
        meta: { title: "系统设置" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore(); // 获取 store 实例
  const token = localStorage.getItem("token");
  const userRole = localStorage.getItem("userRole");

  // 如果要访问登录页或根路径，清除所有认证信息
  if (to.path === "/login" || to.path === "/") {
    userStore.clearUserInfo(); // 清除所有用户信息
    next(); // 继续访问登录页
    return;
  }

  // 检查是否需要认证
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    // 如果没有token，重定向到登录页
    if (!token) {
      next({ path: "/login" });
      return;
    }

    // 检查管理员权限
    if (to.matched.some((record) => record.meta.requiresAdmin)) {
      if (userRole !== "admin") {
        next({ path: "/chat" });
        return;
      }
    }
  }

  // 已登录用户访问登录页面时的重定向
  if (token && (to.path === "/login" || to.path === "/")) {
    if (userRole === "admin") {
      next({ path: "/admin" });
    } else {
      next({ path: "/chat" });
    }
    return;
  }

  next();
});

export default router;
