// src/utils/request.js
export const request = async (url, options = {}) => {
  const token = localStorage.getItem("token");
  const headers = {
    ...options.headers,
    Authorization: `Bearer ${token}`,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    // 401 特殊处理
    if (response.status === 401) {
      window.location.href = "/login";
    }

    // 创建一个自定义错误对象，包含状态码和响应
    const error = new Error(response.statusText);
    error.response = response;
    throw error;
  }

  return response.json();
};
