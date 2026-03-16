# 🦀 FishClaw — 自动化闲鱼智能客服与运营管理平台

> 基于 WebSocket 长连接的闲鱼 7×24 智能客服系统，支持多账号管理、智能回复、自动发货、反风控策略，并可作为 [OpenClaw](https://github.com/anthropics/openclaw) Channel Worker 接入 AI Agent Pipeline。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](https://github.com)

[English README](./README_EN.md) | [使用指南](./docs/USER_GUIDE.md)

---

## ✨ 核心特性

### 智能客服引擎
- **多账号管理** — 独立启停、Cookie 自动刷新、状态实时监控
- **智能回复** — 关键词匹配 → 商品专属回复 → AI 智能回复（多模型支持）
- **自动发货** — 规则匹配、多规格支持、延时发货、防重复
- **商品管理** — 自动收集、详情获取、多规格配置

### 反风控体系
- **设备指纹持久化** — 每账号固定设备 ID，避免多设备关联
- **Per-Account 指纹** — 每账号独立 User-Agent/分辨率，防止多账号关联
- **活跃时间窗口** — 模拟真人作息，非活跃时段延迟回复
- **智能回复延迟** — 基于内容长度的拟人打字速度
- **指数退避重连** — 连接异常时递增等待，避免频繁重连
- **心跳随机抖动** — 消除固定间隔机器特征
- **验证码冷却期** — 通过验证后降频运行
- **请求令牌桶限速** — 控制每分钟回复数

### OpenClaw 集成
- **MCP Server** — 20 个 MCP Tools，支持自然语言操控（Claude Code / OpenClaw Agent）
- **Channel Plugin** — Webhook 架构，买家消息进入 AI Agent Pipeline
- **launchd 托管** — macOS 开机自启 + 崩溃自恢复

### 安全加固
- JWT 认证 + 环境变量密钥管理
- 无硬编码凭据、无测试后门、无明文 Token 日志
- Swagger 文档默认关闭
- IP 防伪造 + 暴力破解防护（5次/5分钟）

---

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 16+（用于 PyExecJS）
- macOS / Linux / Windows

### 安装

```bash
git clone https://github.com/haiyuzhong1980/FishClaw.git
cd FishClaw

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 安装 Playwright 浏览器（商品搜索功能需要）
playwright install chromium
```

### 配置

```bash
# 创建环境变量文件
cat > .env << 'EOF'
SECRET_ENCRYPTION_KEY=your-fernet-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# 可选: OpenClaw 集成
OPENCLAW_ENABLED=false
OPENCLAW_WEBHOOK_URL=http://localhost:18789/plugins/xianyu-channel/inbound
OPENCLAW_WEBHOOK_SECRET=your-webhook-secret

# 可选: 活跃时间窗口
ACTIVE_HOURS_START=7
ACTIVE_HOURS_END=23

# 可选: 启用 Swagger 文档
ENABLE_DOCS=false
EOF

# 生成 Fernet 密钥
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 生成 JWT 密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 启动

```bash
python Start.py
# 访问: http://localhost:8090
# 默认管理员: admin / admin123（首次登录后请立即修改密码）
```

### Docker 部署

```bash
docker compose up -d --build
# 访问: http://localhost:9000
```

---

## 📖 使用指南

### 1. 添加闲鱼账号
1. 登录管理后台
2. 进入「账号管理」→「添加账号」
3. 在闲鱼网页端 F12 → Network → 任意请求 → 复制 Cookie
4. 粘贴 Cookie，保存并启用

### 2. 配置自动回复
- **关键词回复**: 设置"你好" → "您好！宝贝都可以拍，秒发货~"
- **商品专属回复**: 为特定商品设置专门回复
- **AI 回复**: 配置 OpenAI 兼容 API（通义千问/DeepSeek/GPT 等）
- **默认回复**: 未匹配时的兜底回复

### 3. 配置自动发货
1. 添加卡券（文本/批量数据/API/图片）
2. 创建发货规则，匹配商品关键词
3. 买家付款后自动触发发货

### 4. 反风控配置
- **活跃时间**: 环境变量 `ACTIVE_HOURS_START=7` / `ACTIVE_HOURS_END=23`
- **多账号隔离**: 系统自动为每账号生成独立指纹，建议配合独立代理 IP
- **回复延迟**: 自动根据消息长度计算拟人延迟（2-60 秒）

### 5. OpenClaw 集成（可选）

```bash
# 启用消息推送到 OpenClaw
export OPENCLAW_ENABLED=true

# MCP Server 使用（在 Claude Code 中）
# "查看闲鱼账号" → 调用 xianyu_list_accounts
# "添加关键词" → 调用 xianyu_add_keyword
```

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│              OpenClaw 平台（可选）                │
│  MCP Server (20 tools) ←→ Channel Plugin        │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              FishClaw 服务层                     │
│  FastAPI REST API (localhost:8090)               │
│  WebSocket ←→ 闲鱼平台 (wss://goofish)          │
│  SQLite + Cookie 管理 + 反风控引擎               │
└─────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
FishClaw/
├── Start.py                    # 启动入口
├── XianyuAutoAsync.py          # WebSocket 连接 + 消息处理核心
├── reply_server.py             # FastAPI Web 服务器
├── db_manager.py               # SQLite 数据库管理
├── cookie_manager.py           # 多账号 Cookie 管理
├── ai_reply_engine.py          # AI 智能回复引擎
├── config.py                   # 全局配置
├── global_config.yml           # 运行参数配置
├── scripts/
│   ├── start-xianyu.sh         # launchd 启动脚本
│   └── stop-xianyu.sh          # 停止脚本
├── utils/
│   ├── xianyu_utils.py         # 签名/加密/设备指纹
│   ├── xianyu_slider_stealth.py # 滑块验证（反检测）
│   └── ...
├── static/                     # Web 前端
├── data/                       # SQLite 数据库（运行时创建）
└── logs/                       # 日志文件
```

---

## ⚙️ 配置说明

### 环境变量

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `SECRET_ENCRYPTION_KEY` | ✅ | — | Fernet 加密密钥 |
| `JWT_SECRET_KEY` | ✅ | — | JWT 签名密钥 |
| `API_HOST` | — | `0.0.0.0` | 监听地址 |
| `API_PORT` | — | `8090` | 监听端口 |
| `ENABLE_DOCS` | — | `false` | 启用 Swagger 文档 |
| `OPENCLAW_ENABLED` | — | `false` | 启用 OpenClaw 集成 |
| `ACTIVE_HOURS_START` | — | `7` | 活跃时间开始（小时） |
| `ACTIVE_HOURS_END` | — | `23` | 活跃时间结束（小时） |

### global_config.yml 关键参数

- `HEARTBEAT_INTERVAL: 15` — 心跳间隔（自动 ±3s 抖动）
- `TOKEN_REFRESH_INTERVAL: 72000` — Token 刷新间隔（20 小时）
- `ACTIVE_HOURS` — 活跃时间窗口配置

---

## 🔒 安全说明

- 所有凭据通过环境变量管理，不写入代码或配置文件
- Cookie 使用 Fernet 对称加密存储在数据库
- JWT 认证 + 暴力破解防护（5 次/5 分钟 IP 限制）
- 无后门、无硬编码测试密钥
- Token/Cookie 日志输出自动掩码
- Swagger 文档默认关闭

---

## 🙏 致谢

FishClaw 基于以下优秀开源项目构建并进行了深度安全加固与功能增强:

- **[XianyuAutoAgent](https://github.com/shaxiu/XianyuAutoAgent)** — 闲鱼智能客服机器人，提供了核心架构思路
- **[xianyu-auto-reply](https://github.com/zhinianboke-new/xianyu-auto-reply)** — 闲鱼自动回复系统原始项目
- **[xianyu-auto-reply-fix](https://github.com/GuDong2003/xianyu-auto-reply-fix)** — 社区增强版，提供了多用户/多账号/自动发货等企业级功能
- **[XianYuApis](https://github.com/cv-cat/XianYuApis)** — 闲鱼 API 接口技术参考
- **[myfish](https://github.com/Kaguya233qwq/myfish)** — 扫码登录实现参考
- **[OpenClaw](https://github.com/anthropics/openclaw)** — AI Agent 平台，提供了 MCP/Channel Plugin 集成架构

---

## ⚠️ 免责声明

本项目仅供学习与研究使用，严禁商业用途。使用者需自行承担部署、配置和运行风险，并确保实际用途符合当地法律法规和平台规则。

---

## 📄 License

[MIT](./LICENSE)
