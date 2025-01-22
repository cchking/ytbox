import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";

// Element Plus
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import zhCn from "element-plus/dist/locale/zh-cn.mjs";
import "./style/global.css";

// Tailwind CSS
import "./assets/main.css";
import "@fortawesome/fontawesome-free/css/all.min.css";

// Markdown 相关
import { marked } from "marked";
import hljs from "highlight.js";
import "highlight.js/styles/github.css";
import "katex/dist/katex.css";

// 配置 highlight.js
hljs.configure({
  ignoreUnescapedHTML: true,
});

// 配置 marked
const renderer = new marked.Renderer();

// 修改代码块渲染器
renderer.code = (code, lang) => {
  // 处理代码块对象
  let finalCode = code;
  let language = lang;

  // 检查是否是代码块对象
  if (typeof code === "object") {
    try {
      // 如果是代码块对象，提取实际的代码内容
      if (code.raw && code.text) {
        // 移除代码块标记
        finalCode = code.text
          .replace(/^```.*\n?/, "")
          .replace(/```$/, "")
          .trim();
        // 使用对象中的语言信息
        language = code.lang || language;
      } else {
        // 如果不是预期的格式，转为JSON字符串
        finalCode = JSON.stringify(code, null, 2);
      }
    } catch (e) {
      finalCode = String(code);
    }
  }

  // 确保语言有效
  const validLanguage =
    language && hljs.getLanguage(language) ? language : "plaintext";

  try {
    // 进行代码高亮
    const highlighted = hljs.highlight(finalCode, {
      language: validLanguage,
    }).value;

    // 返回带高亮的HTML
    return `<pre><code class="hljs language-${validLanguage}">${highlighted}</code></pre>`;
  } catch (e) {
    console.error("Highlight error:", e);
    // 如果高亮失败，返回未高亮的代码
    return `<pre><code class="hljs language-${validLanguage}">${finalCode}</code></pre>`;
  }
};

// 配置 marked 选项
marked.setOptions({
  renderer: renderer,
  highlight: function (code, lang) {
    let finalCode = code;
    let language = lang;

    // 检查是否是代码块对象
    if (typeof code === "object") {
      try {
        if (code.raw && code.text) {
          finalCode = code.text.trim();
          language = code.lang || language;
        } else {
          finalCode = JSON.stringify(code, null, 2);
        }
      } catch (e) {
        finalCode = String(code);
      }
    }

    // 进行高亮
    try {
      if (language && hljs.getLanguage(language)) {
        return hljs.highlight(finalCode, { language }).value;
      }
      return hljs.highlightAuto(finalCode).value;
    } catch (e) {
      console.error("Highlight error:", e);
      return finalCode;
    }
  },
  gfm: true,
  breaks: true,
  langPrefix: "hljs language-",
  headerIds: false,
  mangle: false,
});

// 创建应用实例
const app = createApp(App);
const pinia = createPinia();

// 使用插件
app.use(pinia);
app.use(router);
app.use(ElementPlus, {
  locale: zhCn,
});

// 注册全局marked方法
app.config.globalProperties.$marked = (content) => {
  if (!content) return "";

  try {
    // 处理代码块对象
    if (typeof content === "object") {
      if (content.type === "code" && content.text) {
        return marked(
          "```" + (content.lang || "") + "\n" + content.text + "\n```"
        );
      }
      return marked(JSON.stringify(content, null, 2));
    }
    return marked(String(content));
  } catch (error) {
    console.error("Markdown parsing error:", error);
    return String(content);
  }
};

// 错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error("Vue Error:", err);
  console.error("Error Info:", info);
};

// 性能提示
app.config.performance = true;

// 获取前端设置
const fetchFrontendSettings = async () => {
  try {
    const response = await fetch("/api/frontend-settings");
    const data = await response.json();

    // 更新标题
    if (data.title) {
      document.title = data.title;
    }

    // 更新网站图标
    if (data.logo) {
      let favicon = document.querySelector('link[rel="icon"]');
      if (!favicon) {
        favicon = document.createElement("link");
        favicon.rel = "icon";
        document.head.appendChild(favicon);
      }
      favicon.href = data.logo;
    }
  } catch (error) {
    console.error("Error loading frontend settings:", error);
  }
};

// 在挂载应用前获取设置
Promise.all([fetchFrontendSettings()])
  .then(() => {
    // 挂载应用
    app.mount("#app");
  })
  .catch((error) => {
    console.error("Error during initialization:", error);
    // 即使出错也要挂载应用
    app.mount("#app");
  });
