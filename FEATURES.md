# Grok2API Ultimate - 功能说明

## 整合的三大项目

### 1. chenyme/grok2api (基础框架)
- ✅ 完整的 OpenAI 兼容 API
- ✅ 工具调用 (Function Calling)
- ✅ Responses API  
- ✅ 视频生成和超分
- ✅ 图片生成和编辑
- ✅ 多存储后端 (local/Redis/MySQL/PostgreSQL)
- ✅ 完善的管理后台
- ✅ 已验证的高并发性能 (1000次/50并发 90.9%成功率)

### 2. DeVibe-one/grok2api_new (真实上下文)
- ✅ 真实多轮对话 (conversationId + responseId)
- ✅ 跨账号会话续接 (Share + Clone机制)
- ✅ 自动识别会话 (消息哈希匹配)
- ✅ 智能冷却机制
- ✅ 搜索过程展示

### 3. TQZHR/grok2api (自动化增强)
- ✅ 自动注册 Token
- ✅ 移动端全适配
- ✅ 增强的 Token 管理
- ✅ 增强的 API Key 管理

## 核心优势

### 1. 性能稳定
基于 chenyme 原版，已通过压力测试：
- 1000 请求 / 50 并发 → 90.9% 成功率
- 平均响应时间 6.04s
- QPS 可达 7.85

### 2. 智能上下文
来自 DeVibe-one 的真实上下文管理：
- 不重发历史消息，节省 Token
- 支持跨账号无缝续接
- 自动识别会话，无需客户端管理

### 3. 自动化运维
来自 TQZHR 的自动注册：
- 批量自动注册账号
- 自动配置 TOS + 年龄 + NSFW
- 支持 Turnstile Solver 或 YesCaptcha

## 使用场景

### 场景 1: 高并发生产环境
- 使用 chenyme 基础功能
- 部署到 VPS + Redis
- 多 Token 轮询
- 适合：API 服务商、企业内部服务

### 场景 2: 长对话应用
- 启用 DeVibe-one 真实上下文
- 节省 Token 消耗
- 支持跨账号续接
- 适合：聊天机器人、客服系统

### 场景 3: 个人自动化
- 启用 TQZHR 自动注册
- 批量生成账号
- 自动维护 Token 池
- 适合：个人开发者、小团队

## 部署建议

### 小规模 (<100 请求/天)
```bash
# 本地部署，local 存储
docker compose up -d
```

### 中规模 (100-1000 请求/天)
```bash
# Docker + Redis
# 启用真实上下文
# 多 Token 轮询
```

### 大规模 (>1000 请求/天)
```bash
# Docker + PostgreSQL
# 启用真实上下文
# 自动注册维护 Token 池
# 负载均衡
```

## 配置选项

### 基础配置 (config.defaults.toml)
```toml
[server]
host = "0.0.0.0"
port = 8000
workers = 1
storage_type = "local"  # local, redis, mysql, pgsql

[app]
key = "grok2api"  # 管理密码
stream = true
```

### 真实上下文 (可选)
```toml
[context]
enabled = true  # 启用真实上下文
conversation_ttl = 72000  # 会话存活时间 (20小时)
max_conversations_per_token = 100
```

### 自动注册 (可选)
```toml
[register]
enabled = true  # 启用自动注册
worker_domain = "grok.com"
email_domain = "example.com"
solver_url = "http://localhost:5000"
default_count = 100
default_concurrency = 10
```

## 功能对比

| 功能 | chenyme | DeVibe-one | TQZHR | Ultimate |
|------|---------|------------|-------|----------|
| OpenAI API | ✅ | ✅ | ✅ | ✅ |
| 工具调用 | ✅ | ❌ | ✅ | ✅ |
| 视频生成 | ✅ | ❌ | ✅ | ✅ |
| 真实上下文 | ❌ | ✅ | ❌ | ✅ |
| 跨账号续接 | ❌ | ✅ | ❌ | ✅ |
| 自动注册 | ❌ | ❌ | ✅ | ✅ |
| 移动端优化 | ❌ | ❌ | ✅ | ✅ |
| 高并发 | ✅ | ❓ | ❌ | ✅ |

## 下一步

1. 解压项目
2. 查看 README.md
3. 根据需求启用功能
4. 部署测试
5. 生产环境上线
