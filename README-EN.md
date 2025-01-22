# YTBOX Project
English | [中文](./README.md)

## Project Introduction
YTBOX is a one-stop AI service platform project.

Demo: https://chatyt.icu

## Main Features
- 👥 User System
  - Account Management
  - VIP Membership
  - Points System
  - OAuth Login (supports GitHub and Linux.do login)

- 💬 Chat Functionality
  - Streamed Responses
  - Conversation Management
  - Folder Organization
  - History Records
  - Multi-modal Conversations

- 🤖 AI Models
  - Multi-channel Access
  - Load Balancing
  - Health Check
  - Usage Statistics
  - Image Generation
  - Video Generation

- 🏪 Model Marketplace
  - Users can publish their own models
  - Support for model transactions with coins
  - Model Rating System
  - Private Deployment Functionality
  - Model Health Monitoring

- 📊 Admin Dashboard 
  - User Management (VIP Duration/Coins/Ban etc.)
  - System Configuration
  - Data Statistics
  - Log Viewing 
  - Channel Configuration
  - Model Configuration
  - Violation Content Monitoring

## Environment Requirements
- Python 3.8+
- SQLite
- Node.js 16+
- npm or yarn

## Quick Start

### Backend Startup
1. Clone the repository:
```bash
git clone https://github.com/cchking/ytbox.git
```

2. Enter the backend directory:
```bash
cd api
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the service:
```bash 
python main.py
```

### Frontend Startup
1. Enter the frontend directory:
```bash
cd chat
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development environment:
```bash
npm run dev
# or
yarn dev
```

4. Build for deployment:
```bash
npm run build
# or
yarn build
```

## Notes
There are still many bugs and features that are not yet implemented. I will continue to maintain the project.

## Author
Mantianxiang

## License
MIT
