# 🦀 FishClaw — Automated Xianyu (Goofish) Intelligent Customer Service & Operations Platform

> A 7×24 intelligent customer service system for Xianyu (Goofish) based on persistent WebSocket connections. Supports multi-account management, AI-powered replies, automated order fulfillment, anti-detection strategies, and integration with [OpenClaw](https://github.com/anthropics/openclaw) as a Channel Worker in the AI Agent Pipeline.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](https://github.com)

[中文 README](./README.md) | [User Guide](./docs/USER_GUIDE.md)

---

## ✨ Core Features

### Intelligent Customer Service Engine
- **Multi-Account Management** — Independent start/stop, automatic Cookie refresh, real-time status monitoring
- **Smart Replies** — Keyword matching → Product-specific replies → AI-powered replies (multi-model support)
- **Automated Order Fulfillment** — Rule-based matching, multi-SKU support, delayed delivery, duplicate prevention
- **Product Management** — Automatic collection, detail fetching, multi-SKU configuration

### Anti-Detection System
- **Device Fingerprint Persistence** — Fixed device ID per account, prevents multi-device association
- **Per-Account Fingerprinting** — Unique User-Agent/resolution per account, prevents cross-account linking
- **Active Hours Window** — Simulates human work patterns, delayed replies during inactive periods
- **Smart Reply Delay** — Human-like typing speed calculated from message length
- **Exponential Backoff Reconnect** — Progressive wait on connection errors, avoids rapid reconnection
- **Heartbeat Jitter** — Randomized intervals eliminate fixed-pattern machine signatures
- **Captcha Cooldown** — Reduced frequency mode after captcha verification
- **Token Bucket Rate Limiting** — Controls replies per minute

### OpenClaw Integration
- **MCP Server** — 20 MCP Tools for natural language control (Claude Code / OpenClaw Agent)
- **Channel Plugin** — Webhook architecture routes buyer messages into the AI Agent Pipeline
- **launchd Management** — macOS auto-start on boot + crash recovery

### Security Hardening
- JWT authentication + environment variable key management
- No hardcoded credentials, no test backdoors, no plaintext Token logging
- Swagger documentation disabled by default
- IP spoofing prevention + brute force protection (5 attempts / 5 minutes)

---

## 🚀 Quick Start

### Requirements
- Python 3.11+
- Node.js 16+ (for PyExecJS)
- macOS / Linux / Windows

### Installation

```bash
git clone https://github.com/haiyuzhong1980/FishClaw.git
cd FishClaw

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browser (required for product search)
playwright install chromium
```

### Configuration

```bash
# Create environment variables file
cat > .env << 'EOF'
SECRET_ENCRYPTION_KEY=your-fernet-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Optional: OpenClaw integration
OPENCLAW_ENABLED=false
OPENCLAW_WEBHOOK_URL=http://localhost:18789/plugins/xianyu-channel/inbound
OPENCLAW_WEBHOOK_SECRET=your-webhook-secret

# Optional: Active hours window
ACTIVE_HOURS_START=7
ACTIVE_HOURS_END=23

# Optional: Enable Swagger docs
ENABLE_DOCS=false
EOF

# Generate Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Start

```bash
python Start.py
# Access: http://localhost:8090
# Default admin: admin / admin123 (change immediately after first login)
```

### Docker Deployment

```bash
docker compose up -d --build
# Access: http://localhost:9000
```

---

## 📖 Usage Guide

### 1. Add a Xianyu Account
1. Log in to the management console
2. Go to "Account Management" → "Add Account"
3. On the Xianyu web page, press F12 → Network → any request → copy the Cookie header value
4. Paste the Cookie, save and enable the account

### 2. Configure Auto-Reply
- **Keyword Reply**: Set "hello" → "Hi! All items are available, instant delivery~"
- **Product-Specific Reply**: Configure dedicated replies for specific products
- **AI Reply**: Configure an OpenAI-compatible API (Qwen / DeepSeek / GPT, etc.)
- **Default Reply**: Fallback reply when no rules match

### 3. Configure Automated Fulfillment
1. Add card/coupon inventory (text / bulk data / API / image)
2. Create fulfillment rules matched by product keywords
3. Fulfillment triggers automatically after buyer payment

### 4. Anti-Detection Configuration
- **Active Hours**: Set via `ACTIVE_HOURS_START=7` / `ACTIVE_HOURS_END=23`
- **Multi-Account Isolation**: System auto-generates unique fingerprints per account; recommended with dedicated proxy IPs
- **Reply Delay**: Automatically calculates human-like delay (2–60 seconds) based on message length

### 5. OpenClaw Integration (Optional)

```bash
# Enable message forwarding to OpenClaw
export OPENCLAW_ENABLED=true

# MCP Server usage (in Claude Code)
# "List Xianyu accounts" → calls xianyu_list_accounts
# "Add keyword" → calls xianyu_add_keyword
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│              OpenClaw Platform (Optional)        │
│  MCP Server (20 tools) ←→ Channel Plugin        │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              FishClaw Service Layer              │
│  FastAPI REST API (localhost:8090)               │
│  WebSocket ←→ Xianyu Platform (wss://goofish)   │
│  SQLite + Cookie Manager + Anti-Detection Engine │
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
FishClaw/
├── Start.py                    # Application entry point
├── XianyuAutoAsync.py          # WebSocket connection + message handling core
├── reply_server.py             # FastAPI web server
├── db_manager.py               # SQLite database management
├── cookie_manager.py           # Multi-account Cookie manager
├── ai_reply_engine.py          # AI reply engine
├── config.py                   # Global configuration
├── global_config.yml           # Runtime parameter configuration
├── scripts/
│   ├── start-xianyu.sh         # launchd startup script
│   └── stop-xianyu.sh          # Stop script
├── utils/
│   ├── xianyu_utils.py         # Signing / encryption / device fingerprinting
│   ├── xianyu_slider_stealth.py # Slider captcha (anti-detection)
│   └── ...
├── static/                     # Web frontend
├── data/                       # SQLite database (created at runtime)
└── logs/                       # Log files
```

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_ENCRYPTION_KEY` | ✅ | — | Fernet encryption key |
| `JWT_SECRET_KEY` | ✅ | — | JWT signing key |
| `API_HOST` | — | `0.0.0.0` | Bind address |
| `API_PORT` | — | `8090` | Bind port |
| `ENABLE_DOCS` | — | `false` | Enable Swagger documentation |
| `OPENCLAW_ENABLED` | — | `false` | Enable OpenClaw integration |
| `ACTIVE_HOURS_START` | — | `7` | Active hours start (hour of day) |
| `ACTIVE_HOURS_END` | — | `23` | Active hours end (hour of day) |

### global_config.yml Key Parameters

- `HEARTBEAT_INTERVAL: 15` — Heartbeat interval (auto ±3s jitter)
- `TOKEN_REFRESH_INTERVAL: 72000` — Token refresh interval (20 hours)
- `ACTIVE_HOURS` — Active hours window configuration

---

## 🔒 Security Notes

- All credentials are managed via environment variables — never written to code or config files
- Cookies are stored encrypted using Fernet symmetric encryption
- JWT authentication + brute force protection (5 attempts / 5 minutes per IP)
- No backdoors, no hardcoded test keys
- Token/Cookie log output is automatically masked
- Swagger documentation is disabled by default

---

## 🙏 Acknowledgements

FishClaw is built upon the following excellent open-source projects, with deep security hardening and feature enhancements applied:

- **[XianyuAutoAgent](https://github.com/shaxiu/XianyuAutoAgent)** — Xianyu intelligent customer service bot, provided core architectural ideas
- **[xianyu-auto-reply](https://github.com/zhinianboke-new/xianyu-auto-reply)** — Original Xianyu auto-reply system
- **[xianyu-auto-reply-fix](https://github.com/GuDong2003/xianyu-auto-reply-fix)** — Community-enhanced version with multi-user, multi-account, and automated fulfillment capabilities
- **[XianYuApis](https://github.com/cv-cat/XianYuApis)** — Xianyu API technical reference
- **[myfish](https://github.com/Kaguya233qwq/myfish)** — QR code login implementation reference
- **[OpenClaw](https://github.com/anthropics/openclaw)** — AI Agent platform, provided MCP/Channel Plugin integration architecture

---

## ⚠️ Disclaimer

This project is intended for learning and research purposes only. Commercial use is strictly prohibited. Users are solely responsible for deployment, configuration, and operational risks, and must ensure their actual use complies with local laws and regulations as well as platform terms of service.

---

## 📄 License

[MIT](./LICENSE)
