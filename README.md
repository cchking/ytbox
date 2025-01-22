# YTBOX 项目
[English](./README-EN.md) | 中文

## 项目介绍
YTBOX是一个一站式AI服务平台项目

演示:https://chatyt.icu

## 主要功能
- 👥 用户系统
  - 账号管理
  - VIP 会员
  - 积分系统
  - OAuth 登录（支持Github和Linux.do登录）

- 💬 聊天功能
  - 流式响应
  - 对话管理 
  - 文件夹组织
  - 历史记录
  - 支持多模态对话

- 🤖 AI 模型
  - 多渠道接入
  - 负载均衡
  - 健康检测
  - 使用统计
  - 图片生成
  - 视频生成

- 🏪 模型市场
  - 用户可发布自有模型
  - 支持金币交易模型
  - 模型评分系统
  - 私有部署功能
  - 模型健康监测

- 📊 管理后台 
  - 用户管理（VIP时长/金币/封禁等）
  - 系统配置
  - 数据统计
  - 日志查看 
  - 渠道配置
  - 模型配置
  - 违规内容监控


## 环境要求
- Python 3.8+
- SQLite
- Node.js 16+
- npm 或 yarn

## 快速开始

### 后端启动
1. 克隆代码:
```bash
git clone https://github.com/cchking/ytbox.git
```

2. 进入后端目录:
```bash
cd api
```

3. 安装依赖:
```bash
pip install -r requirements.txt
```

4. 启动服务:
```bash 
python main.py
```

### 前端启动
1. 进入前端目录:
```bash
cd chat
```

2. 安装依赖:
```bash
npm install
# 或
yarn install
```

3. 开发环境启动:
```bash
npm run dev
# 或
yarn dev
```

4. 打包部署:
```bash
npm run build
# 或
yarn build
```

## 注意事项
目前还有许多bug和功能未实现，我会一直维护
outhor登录和研究所功能需要自己在init.py里配置
## 作者
满天翔

## 许可证
MIT
