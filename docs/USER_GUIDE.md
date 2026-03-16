# FishClaw 使用指南

> 完整的安装、配置与运营指南

---

## 目录

1. [安装部署](#1-安装部署)
   - [本地部署](#11-本地部署)
   - [Docker 部署](#12-docker-部署)
   - [launchd 服务（macOS）](#13-launchd-服务macos)
2. [首次配置向导](#2-首次配置向导)
3. [账号管理](#3-账号管理)
4. [自动回复配置](#4-自动回复配置)
5. [自动发货配置](#5-自动发货配置)
6. [反风控最佳实践](#6-反风控最佳实践)
7. [OpenClaw 集成指南](#7-openclaw-集成指南)
8. [API 参考](#8-api-参考)
9. [常见问题 FAQ](#9-常见问题-faq)
10. [故障排除](#10-故障排除)

---

## 1. 安装部署

### 1.1 本地部署

#### 环境准备

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.11+ | 核心运行环境 |
| Node.js | 16+ | PyExecJS 签名计算 |
| Chromium | 最新版 | Playwright 商品搜索 |

```bash
# 验证环境
python --version   # 3.11.x
node --version     # v16.x 或更高
```

#### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/haiyuzhong1980/FishClaw.git
cd FishClaw

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# 3. 安装 Python 依赖
pip install --upgrade pip
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器
playwright install chromium
playwright install-deps chromium   # Linux 需要

# 5. 创建环境变量文件（见第 2 节）
cp .env.example .env   # 如有示例文件
# 或手动创建 .env

# 6. 启动
python Start.py
```

#### 访问

- 管理后台: http://localhost:8090
- 默认账户: `admin` / `admin123`
- **首次登录后立即修改密码**

### 1.2 Docker 部署

#### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

#### 标准部署

```bash
# 创建 .env 文件（必须）
cat > .env << 'EOF'
SECRET_ENCRYPTION_KEY=your-fernet-key-here
JWT_SECRET_KEY=your-jwt-secret-here
EOF

# 启动容器
docker compose up -d --build

# 查看日志
docker compose logs -f xianyu-reply

# 停止
docker compose down
```

访问: http://localhost:9000

#### 国内镜像部署（中国大陆）

```bash
# 使用国内镜像加速
docker compose -f docker-compose-cn.yml up -d --build
```

#### 多架构构建（ARM/x86）

```bash
chmod +x build-multi-arch.sh
./build-multi-arch.sh
```

### 1.3 launchd 服务（macOS）

在 macOS 上配置开机自启并支持崩溃自动恢复：

```bash
# 修改启动脚本中的路径
vim scripts/start-xianyu.sh
# 将 /path/to/FishClaw 替换为实际路径

# 安装服务
cp scripts/com.fishclaw.xianyu.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.fishclaw.xianyu.plist

# 验证状态
launchctl list | grep fishclaw

# 手动启动/停止
launchctl start com.fishclaw.xianyu
launchctl stop com.fishclaw.xianyu

# 卸载服务
launchctl unload ~/Library/LaunchAgents/com.fishclaw.xianyu.plist
```

---

## 2. 首次配置向导

### 步骤 1: 生成加密密钥

```bash
# 生成 Fernet 密钥（Cookie 加密用）
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 生成 JWT 密钥（API 认证用）
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 步骤 2: 创建 .env 文件

```bash
cat > .env << 'EOF'
# ===== 必填项 =====
SECRET_ENCRYPTION_KEY=<上一步生成的 Fernet 密钥>
JWT_SECRET_KEY=<上一步生成的 JWT 密钥>

# ===== 服务配置 =====
API_HOST=0.0.0.0
API_PORT=8090
ENABLE_DOCS=false

# ===== 反风控配置 =====
ACTIVE_HOURS_START=7
ACTIVE_HOURS_END=23

# ===== OpenClaw 集成（可选）=====
OPENCLAW_ENABLED=false
OPENCLAW_WEBHOOK_URL=http://localhost:18789/plugins/xianyu-channel/inbound
OPENCLAW_WEBHOOK_SECRET=your-webhook-secret
EOF
```

### 步骤 3: 修改 global_config.yml

```yaml
# 关键参数说明
HEARTBEAT_INTERVAL: 15        # 心跳间隔（秒）
TOKEN_REFRESH_INTERVAL: 72000 # Token 刷新（秒，约20小时）

ACTIVE_HOURS:
  start: 7    # 活跃开始时间
  end: 23     # 活跃结束时间
```

### 步骤 4: 首次登录与修改密码

1. 访问 http://localhost:8090
2. 使用 `admin` / `admin123` 登录
3. 进入「用户设置」→「修改密码」
4. 设置强密码（建议 16 位以上，含大小写+数字+特殊字符）

---

## 3. 账号管理

### 3.1 获取闲鱼 Cookie

**方法一: 网页端复制（推荐）**

1. 在 Chrome/Edge 中访问 https://www.goofish.com（闲鱼）
2. 登录你的账号
3. 按 F12 → 切换到「Network（网络）」标签
4. 刷新页面，点击任意请求
5. 在「Headers（标头）」中找到 `Cookie:` 字段
6. 复制完整的 Cookie 值（通常很长，包含多个键值对）

**注意事项:**
- Cookie 有效期约 7-30 天，系统会自动尝试刷新
- 不同账号需分别获取各自的 Cookie
- 若账号有设备绑定，可能需要在同一设备上操作

### 3.2 添加账号

1. 登录管理后台
2. 「账号管理」→「添加账号」
3. 填写：
   - **昵称**: 便于识别的账号名
   - **Cookie**: 粘贴完整 Cookie
   - **代理设置**（可选）: `http://user:pass@proxy-host:port`
4. 点击「保存」
5. 切换「启用」开关

### 3.3 多账号最佳实践

```
账号 A: Cookie_A + 代理 IP_A + 设备指纹 A（自动生成）
账号 B: Cookie_B + 代理 IP_B + 设备指纹 B（自动生成）
账号 C: Cookie_C + 代理 IP_C + 设备指纹 C（自动生成）
```

- 每个账号使用独立的代理 IP（避免共享 IP 关联）
- 系统自动为每账号生成独立设备指纹（无需手动配置）
- 建议账号间操作时间错开，避免同时大量回复

### 3.4 Cookie 失效处理

当 Cookie 失效时，后台会显示账号状态为「离线」：

1. 重新获取闲鱼 Cookie
2. 进入账号详情 → 「更新 Cookie」
3. 粘贴新 Cookie → 保存
4. 系统自动重连

---

## 4. 自动回复配置

### 4.1 回复优先级

系统按以下顺序匹配回复规则（高到低）：

```
1. 商品专属关键词（匹配特定商品 + 关键词）
2. 全局关键词（匹配所有商品）
3. 商品专属默认回复
4. AI 智能回复
5. 全局默认回复
```

### 4.2 关键词回复

**添加关键词**

1. 「回复管理」→「关键词设置」→「添加关键词」
2. 填写：
   - **触发词**: 支持多个，换行分隔（如：`你好\n您好\nHi`）
   - **回复内容**: 支持多条随机回复（换行分隔，系统随机选一条）
   - **匹配方式**: 包含 / 完全匹配 / 正则
   - **账号范围**: 全部 / 指定账号

**示例配置**

| 触发词 | 回复内容 |
|--------|----------|
| 你好, 您好, hi, hello | 您好亲，有什么可以帮您的~\n您好！宝贝都可以拍，秒发货 |
| 有货吗, 有没有, 还有吗 | 亲，有货的！现货秒发~ |
| 价格, 多少钱, 能便宜吗 | 亲，价格已经很实惠了，都是诚心出售的好物~ |
| 发货时间, 什么时候发 | 付款后立即自动发货，一般几秒内到账~ |

### 4.3 AI 智能回复

**配置 OpenAI 兼容 API**

1. 「设置」→「AI 配置」
2. 填写：
   - **API 地址**: 如 `https://api.deepseek.com/v1`
   - **API Key**: 你的 API 密钥
   - **模型**: 如 `deepseek-chat`、`qwen-turbo`、`gpt-4o-mini`
   - **系统 Prompt**: 定义 AI 角色和回复风格

**推荐系统 Prompt**

```
你是一个专业的闲鱼客服，负责回答买家的问题。
请保持友好、专业的态度，回复要简洁有用（50字以内）。
如果买家问价格，告知价格已是最低价，支持快速付款。
如果买家问发货，告知付款后自动发货，立即到账。
不要承诺任何无法实现的事情。
```

### 4.4 商品专属回复

针对特定商品配置专属回复，优先级最高：

1. 「商品管理」→ 选择商品 → 「专属回复」
2. 为该商品设置特定关键词和回复内容
3. 适用场景：不同商品有不同的规格说明、发货方式等

---

## 5. 自动发货配置

### 5.1 卡券类型

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| 文本卡密 | 单条固定文本 | 兑换码、序列号 |
| 批量数据 | 多行卡密（每行一条） | 大量卡密库存 |
| API 接口 | 调用外部 API 获取卡密 | 动态库存系统 |
| 图片 | 发送图片文件 | 图片验证码、二维码 |

### 5.2 添加卡券

**文本/批量卡密**

1. 「发货管理」→「卡券库存」→「添加卡券」
2. 选择类型「批量数据」
3. 在文本框中粘贴卡密（每行一条）
4. 保存后系统自动统计剩余数量

**API 类型**

```json
{
  "url": "https://your-api.com/get-card",
  "method": "POST",
  "headers": {"Authorization": "Bearer your-token"},
  "body": {"product_id": "{{product_id}}"},
  "response_path": "data.card_code"
}
```

### 5.3 发货规则

1. 「发货管理」→「发货规则」→「添加规则」
2. 配置：
   - **商品关键词**: 匹配商品标题中的关键词
   - **卡券库存**: 选择对应的卡券
   - **触发条件**: 付款成功（推荐）/ 下单
   - **延时发货**: 0-300 秒（防止风控，建议 5-30 秒）
   - **发货消息模板**: 支持变量占位符

**发货消息模板示例**

```
亲，您的订单已自动发货！

卡密: {{card_code}}

使用方法：
1. 打开对应平台
2. 在兑换码处输入上方卡密
3. 确认兑换即可

如有问题请联系客服，感谢购买~
```

### 5.4 多规格发货

针对同一商品的不同规格配置不同卡券：

1. 商品规格 A → 卡券库存 A
2. 商品规格 B → 卡券库存 B
3. 系统根据买家选择的规格自动匹配

---

## 6. 反风控最佳实践

### 6.1 活跃时间窗口

模拟真实卖家的在线时间，非活跃时段消息会被延迟处理：

```bash
# .env 配置
ACTIVE_HOURS_START=7   # 早 7 点开始活跃
ACTIVE_HOURS_END=23    # 晚 11 点停止活跃
```

非活跃时段（23:00 - 7:00）策略：
- 收到消息记录但延迟回复
- 在活跃时段开始时批量处理积压消息
- 避免凌晨 3 点秒回显得异常

### 6.2 设备指纹隔离

系统自动为每个账号生成并持久化独立设备指纹：

- **设备 ID**: UUID v4，首次生成后固定不变
- **User-Agent**: 基于账号 ID 的哈希生成，每账号唯一
- **屏幕分辨率**: 从常见分辨率池中为每账号固定选取

无需手动配置，但需注意：
- **不要**在多台机器上同时运行同一账号
- **不要**频繁更换运行机器
- 若必须迁移，导出账号数据时会保留指纹信息

### 6.3 代理 IP 策略

强烈建议多账号配合独立代理 IP：

```
# 住宅代理（最优）
http://user:pass@residential-proxy:port

# 数据中心代理（次选）
http://user:pass@datacenter-proxy:port

# 建议：每个账号固定使用同一 IP（避免频繁切换）
```

代理配置入口：账号管理 → 编辑账号 → 代理设置

### 6.4 回复频率控制

系统内置令牌桶限速：

```yaml
# global_config.yml
RATE_LIMIT:
  max_per_minute: 20      # 每分钟最大回复数
  burst_size: 5           # 突发上限
```

建议值：
- 新账号（<1个月）: 每分钟 ≤10 条
- 成熟账号（>3个月）: 每分钟 ≤20 条
- 高信用账号: 每分钟 ≤30 条

### 6.5 回复延迟配置

系统自动计算拟人延迟，无需手动调整：

- 短消息（<20字）: 2-5 秒
- 中等消息（20-100字）: 5-15 秒
- 长消息（>100字）: 15-60 秒

### 6.6 心跳与重连

- **心跳抖动**: ±3 秒随机化，消除固定间隔特征
- **指数退避**: 断线后 2s → 4s → 8s → ... → 最大 300s 重连等待
- **验证码冷却**: 遇到验证码后降频运行 30 分钟

---

## 7. OpenClaw 集成指南

### 7.1 架构概览

```
买家消息
    │
    ▼
FishClaw WebSocket
    │
    ├─── 直接处理（关键词/AI回复）
    │
    └─── Webhook 推送到 OpenClaw
              │
              ▼
         OpenClaw Channel Plugin
              │
              ▼
         AI Agent Pipeline
              │
              ▼
         生成回复 → FishClaw API → 发送给买家
```

### 7.2 配置 Channel Plugin

```bash
# .env 中启用
OPENCLAW_ENABLED=true
OPENCLAW_WEBHOOK_URL=http://localhost:18789/plugins/xianyu-channel/inbound
OPENCLAW_WEBHOOK_SECRET=your-32-char-secret
```

在 OpenClaw 后台配置 Channel Plugin：
- Channel ID: `xianyu`
- Inbound URL: `http://fishclaw-host:8090/webhook/openclaw`
- Secret: 与 `OPENCLAW_WEBHOOK_SECRET` 一致

### 7.3 MCP Server 配置

在 Claude Code 中添加 FishClaw MCP Server：

```json
// ~/.claude.json 或 .mcp.json
{
  "mcpServers": {
    "fishclaw": {
      "command": "python",
      "args": ["/path/to/FishClaw/mcp_server.py"],
      "env": {
        "FISHCLAW_API_URL": "http://localhost:8090",
        "FISHCLAW_API_KEY": "your-jwt-token"
      }
    }
  }
}
```

### 7.4 可用 MCP Tools（20 个）

| 工具名 | 功能 |
|--------|------|
| `xianyu_list_accounts` | 列出所有账号 |
| `xianyu_get_account` | 获取账号详情 |
| `xianyu_enable_account` | 启用账号 |
| `xianyu_disable_account` | 禁用账号 |
| `xianyu_list_keywords` | 列出关键词规则 |
| `xianyu_add_keyword` | 添加关键词 |
| `xianyu_update_keyword` | 更新关键词 |
| `xianyu_delete_keyword` | 删除关键词 |
| `xianyu_list_products` | 列出商品 |
| `xianyu_get_product` | 获取商品详情 |
| `xianyu_list_orders` | 列出订单 |
| `xianyu_get_order` | 获取订单详情 |
| `xianyu_list_cards` | 列出卡券库存 |
| `xianyu_add_cards` | 添加卡券 |
| `xianyu_get_stats` | 获取统计数据 |
| `xianyu_send_message` | 手动发送消息 |
| `xianyu_get_conversations` | 获取会话列表 |
| `xianyu_get_messages` | 获取消息历史 |
| `xianyu_get_fulfillment_rules` | 获取发货规则 |
| `xianyu_trigger_fulfillment` | 手动触发发货 |

**使用示例（在 Claude Code 中）**

```
用户: 帮我查看闲鱼所有账号的状态
Claude: [调用 xianyu_list_accounts] → 返回账号列表和状态

用户: 把"你好"的回复改成"您好，很高兴为您服务！"
Claude: [调用 xianyu_update_keyword] → 更新成功

用户: 查看今天的回复统计
Claude: [调用 xianyu_get_stats] → 返回今日数据
```

### 7.5 Agent 配置建议

在 OpenClaw 中配置闲鱼智能客服 Agent：

```yaml
agent:
  name: 闲鱼智能客服
  model: claude-3-5-haiku  # 快速响应
  system_prompt: |
    你是专业的闲鱼客服助手。
    回复要简洁（50字以内），友好专业。
    遇到价格问题：坚守定价，可提供小额优惠。
    遇到发货问题：告知付款后自动发货。
    遇到商品问题：提供详细的商品说明。
  tools:
    - fishclaw:xianyu_send_message
    - fishclaw:xianyu_get_product
```

---

## 8. API 参考

所有 API 需要 JWT 认证（在登录后获取 Token）：

```bash
# 获取 Token
curl -X POST http://localhost:8090/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# 响应
{"token": "eyJhbGci...", "expires_in": 86400}

# 使用 Token
curl http://localhost:8090/api/accounts \
  -H "Authorization: Bearer eyJhbGci..."
```

### 主要端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录获取 Token |
| GET | `/api/accounts` | 账号列表 |
| POST | `/api/accounts` | 添加账号 |
| PUT | `/api/accounts/{id}` | 更新账号 |
| DELETE | `/api/accounts/{id}` | 删除账号 |
| POST | `/api/accounts/{id}/enable` | 启用账号 |
| POST | `/api/accounts/{id}/disable` | 禁用账号 |
| GET | `/api/keywords` | 关键词列表 |
| POST | `/api/keywords` | 添加关键词 |
| PUT | `/api/keywords/{id}` | 更新关键词 |
| DELETE | `/api/keywords/{id}` | 删除关键词 |
| GET | `/api/products` | 商品列表 |
| GET | `/api/orders` | 订单列表 |
| GET | `/api/cards` | 卡券列表 |
| POST | `/api/cards` | 添加卡券 |
| GET | `/api/stats` | 统计数据 |
| GET | `/api/conversations` | 会话列表 |
| GET | `/api/conversations/{id}/messages` | 消息历史 |
| POST | `/api/messages/send` | 手动发送消息 |

启用 Swagger 文档（仅开发环境）：

```bash
ENABLE_DOCS=true python Start.py
# 访问: http://localhost:8090/docs
```

---

## 9. 常见问题 FAQ

### Q: Cookie 多久会失效？

A: 闲鱼 Cookie 通常有效期为 7-30 天。系统会在 Cookie 即将失效前自动尝试刷新。若刷新失败，账号状态会变为「离线」，需手动更新 Cookie。

### Q: 可以同时运行多少个账号？

A: 理论上无上限，实际取决于服务器资源。建议单机运行 ≤10 个账号以保证稳定性。每个账号会持续保持 WebSocket 连接。

### Q: AI 回复支持哪些模型？

A: 支持任何兼容 OpenAI API 格式的模型，包括：
- 阿里云通义千问（推荐，国内访问快）
- DeepSeek（性价比高）
- OpenAI GPT-4o / GPT-4o-mini
- 本地部署的 Ollama 等

### Q: 自动发货失败怎么办？

A: 检查以下几点：
1. 卡券库存是否充足
2. 发货规则是否正确匹配商品
3. 查看日志 `logs/fulfillment.log` 中的错误信息
4. 手动在管理后台触发补发

### Q: 遇到验证码怎么处理？

A: 系统会自动尝试处理滑块验证码。若无法自动通过：
1. 管理后台会显示验证码提示
2. 点击「处理验证码」按钮
3. 手动完成验证
4. 系统进入冷却期（30分钟降频运行）

### Q: 如何备份数据？

A: 数据存储在 `data/xianyu_data.db` 中（SQLite 文件）：

```bash
# 手动备份
cp data/xianyu_data.db backups/xianyu_data_$(date +%Y%m%d).db

# 恢复
cp backups/xianyu_data_20250101.db data/xianyu_data.db
```

### Q: 消息发出去了但买家说没收到？

A: 可能原因：
1. 闲鱼平台延迟（通常 1-5 秒）
2. 买家网络问题
3. 消息被平台过滤（内容触发关键词）

建议检查后台「消息日志」确认发送状态。

---

## 10. 故障排除

### 10.1 服务启动失败

**问题**: `python Start.py` 报错

**排查**:
```bash
# 检查 Python 版本
python --version

# 检查依赖是否完整
pip install -r requirements.txt

# 检查环境变量
cat .env

# 查看详细错误
python Start.py 2>&1 | head -50
```

常见原因：
- `.env` 文件不存在或格式错误
- `SECRET_ENCRYPTION_KEY` / `JWT_SECRET_KEY` 未设置
- 端口 8090 已被占用（`lsof -i :8090`）

### 10.2 账号显示离线

**排查顺序**:

1. Cookie 是否有效（在浏览器访问闲鱼验证）
2. 代理 IP 是否可用（`curl -x proxy:port https://goofish.com`）
3. 查看账号日志：「账号管理」→ 点击账号 → 「查看日志」
4. 尝试「重新连接」

### 10.3 回复消息未发出

**检查**:

1. 账号是否在线（绿色状态）
2. 是否在活跃时间窗口内
3. 是否触发了速率限制（查看 `logs/rate_limit.log`）
4. 关键词规则是否配置正确

```bash
# 实时查看日志
tail -f realtime.log | grep "reply"
```

### 10.4 自动发货未触发

**检查清单**:

- [ ] 发货规则是否启用
- [ ] 商品关键词是否与规则匹配
- [ ] 卡券库存是否 > 0
- [ ] 触发条件是否满足（付款确认需要平台回调）

```bash
# 查看发货日志
grep "fulfillment" logs/*.log | tail -20
```

### 10.5 内存占用过高

**原因**: 长时间运行后消息缓存积累

**解决**:
```bash
# 重启服务
./scripts/stop-xianyu.sh && ./scripts/start-xianyu.sh

# 或定时重启（在 crontab 或 launchd 中配置）
0 4 * * * /path/to/FishClaw/scripts/stop-xianyu.sh && /path/to/FishClaw/scripts/start-xianyu.sh
```

### 10.6 数据库损坏

```bash
# 验证数据库完整性
python -c "import sqlite3; conn = sqlite3.connect('data/xianyu_data.db'); conn.execute('PRAGMA integrity_check'); print('OK')"

# 从备份恢复
cp backups/xianyu_data_<日期>.db data/xianyu_data.db
```

### 10.7 获取帮助

- 查看项目 Issues: https://github.com/haiyuzhong1980/FishClaw/issues
- 查看日志文件: `logs/` 目录
- 启用详细日志: 在 `global_config.yml` 中设置 `LOG_LEVEL: DEBUG`
