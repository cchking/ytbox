// global.js
import { ElMessage } from "element-plus";
import { nextTick } from "vue"; // 从 Vue 框架导入 nextTick

export default {
  install(app) {
    // 将配置应用到应用程序
    app.config.globalProperties.$message = ElMessage;
    // 使用 nextTick 延迟设置属性
    nextTick(() => {
      app.config.globalProperties.$message.defaults.plain = true;
    });
  },
};
