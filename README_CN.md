# Grok2API Ultimate Edition - 使用说明

## 🎯 这个版本的特点

这是整合了三个优秀项目的增强版本：

### 基础功能 (来自 chenyme/grok2api)
✅ 完整的 OpenAI 兼容 API
✅ 工具调用、视频生成、图片生成
✅ 多存储后端支持
✅ 完善的管理后台
✅ **已验证的高并发性能** (1000次/50并发 90.9%成功率)

### 增强功能 (可选启用)

#### 1. 真实上下文管理 (来自 DeVibe-one)
- 不重发历史消息，节省 Token
- 支持跨账号会话续接
- 自动识别会话

**启用方法：**
```toml
# data/config.toml
[context]
enabled = true
conversation_ttl = 72000
max_conversations_per_token = 100
```

**状态：** ⚠️ 已集成模块，需要进一步开发才能完全可用

#### 2. 自动注册 Token (来自 TQZHR)
- 批量自动注册账号
- 自动配置 TOS + 年龄 + NSFW
- 支持 Turnstile Solver 或 YesCaptcha

**启用方法：**
```toml
# data/config.toml
[register]
enabled = true
worker_domain = "grok.com"
email_domain = "example.com"
solver_url = "http://localhost:5000"
default_count = 100
default_concurrency = 10
```

**API 端点：**
- POST `/api/v1/admin/auto-register` - 执行自动注册
- GET `/api/v1/admin/auto-register/status` - 查看状态

**状态：** ✅ 已集成，可用

## 🚀 快速开始

### 1. 基础部署 (5分钟)

```bash
# Docker 部署
docker compose up -d

# 或本地部署
uv sync && uv run main.py
```

访问：http://localhost:8000/admin
默认密码：`grok2api`

### 2. 添加 Token

1. 登录 https://grok.com
2. 浏览器开发者工具 → Cookies → 复制 `sso`
3. 管理后台 → Token 管理 → 添加

### 3. 测试 API

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-test" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

## 📚 详细文档

- **FEATURES.md** - 完整功能说明
- **QUICKSTART.md** - 快速开始指南
- **VERSION.md** - 版本信息和整合说明

## ⚙️ 配置说明

### 基础配置 (必需)

```toml
[server]
host = "0.0.0.0"
port = 8000
storage_type = "local"  # local, redis, mysql, pgsql

[app]
key = "grok2api"  # 管理密码
stream = true
```

### 真实上下文 (可选)

```toml
[context]
enabled = false  # 改为 true 启用
conversation_ttl = 72000
max_conversations_per_token = 100
```

### 自动注册 (可选)

```toml
[register]
enabled = false  # 改为 true 启用
worker_domain = "grok.com"
email_domain = "example.com"
solver_url = "http://localhost:5000"
default_count = 100
default_concurrency = 10
yescaptcha_client_key = ""  # 可选
```

## 🔧 开发状态

### ✅ 完全可用
- chenyme 原版所有功能
- 自动注册 API 端点
- 配置开关

### ⚠️ 部分可用
- 真实上下文管理（模块已集成，需要进一步开发）

### 📝 待完成
- [ ] 完整实现真实上下文到 chat API
- [ ] 管理后台添加自动注册界面
- [ ] 跨账号会话续接实现
- [ ] 完整的测试和文档

## 🤝 贡献

欢迎提交 PR 完善功能！

特别需要：
1. 完整实现真实上下文集成
2. 管理后台 UI 改进
3. 更多测试和文档

## 📄 许可证

MIT License

继承自三个源项目的许可证。

## 🙏 致谢

- [chenyme/grok2api](https://github.com/chenyme/grok2api) - 稳定的基础框架
- [DeVibe-one/grok2api_new](https://github.com/DeVibe-one/grok2api_new) - 智能的上下文管理
- [TQZHR/grok2api](https://github.com/TQZHR/grok2api) - 自动化和移动端优化

## ⚠️ 免责声明

本项目仅供学习和研究使用。请遵守 Grok 的服务条款。
