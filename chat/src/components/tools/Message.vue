<script>
import { ElMessage } from "element-plus";

const Message = {
  // 定义 success 方法
  success(message) {
    ElMessage({
      message, // 使用传入的 message 参数
      type: "success",
      plain: true,
    });
  },
  // 定义 warning 方法
  warning(message) {
    ElMessage({
      message,
      type: "warning",
      plain: true,
    });
  },
  // 定义 info 方法
  info(message) {
    ElMessage({
      message,
      type: "info",
      plain: true,
    });
  },
  // 定义 error 方法
  error(message) {
    ElMessage({
      message,
      type: "error",
      plain: true,
    });
  },
};

export default Message;
</script>
