# 快速开始

## 1. 基础部署 (5分钟)

### Docker 部署 (推荐)

```bash
# 解压
tar -xzf grok2api-ultimate.tar.gz
cd grok2api-ultimate

# 启动
docker compose up -d

# 查看日志
docker compose logs -f
```

访问：http://localhost:8000/admin
默认密码：`grok2api`

### 本地部署

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv sync

# 启动
uv run main.py
```

## 2. 添加 Token

1. 登录 https://grok.com
2. 打开浏览器开发者工具 (F12)
3. Application → Cookies → 复制 `sso` 值
4. 进入管理后台 → Token 管理 → 添加

## 3. 测试 API

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-test" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": false
  }'
```

## 4. 启用高级功能 (可选)

### 启用真实上下文

编辑 `data/config.toml`:

```toml
[context]
enabled = true
conversation_ttl = 72000
max_conversations_per_token = 100
```

重启服务：
```bash
docker compose restart
```

### 启用自动注册

1. 配置 `data/config.toml`:

```toml
[register]
enabled = true
worker_domain = "grok.com"
email_domain = "example.com"
solver_url = "http://localhost:5000"
default_count = 100
default_concurrency = 10
```

2. 启动 Turnstile Solver:

```bash
cd app/services/register/services
python turnstile_solver.py
```

3. 在管理后台使用自动注册功能

## 5. 生产环境配置

### 使用 Redis

编辑 `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:alpine
    restart: unless-stopped
  
  grok2api:
    environment:
      SERVER_STORAGE_TYPE: redis
      SERVER_STORAGE_URL: redis://redis:6379/0
    depends_on:
      - redis
```

### 配置反向代理 (Nginx)

```nginx
server {
    listen 80;
    server_name grok.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

### 启用 HTTPS

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d grok.example.com
```

## 6. 对接客户端

### ChatGPT-Next-Web

```env
OPENAI_API_KEY=sk-test
BASE_URL=http://localhost:8000/v1
```

### LobeChat

设置 → 语言模型 → 添加自定义模型：
- API 地址：http://localhost:8000/v1
- API Key：sk-test
- 模型：grok-4

### OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-test",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="grok-4",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

## 7. 监控和维护

### 查看日志

```bash
# Docker
docker compose logs -f

# 本地
tail -f logs/grok2api.log
```

### 查看统计

访问管理后台 → 请求统计

### 备份数据

```bash
# 备份数据目录
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

### 更新

```bash
# Docker
docker compose pull
docker compose up -d

# 本地
git pull
uv sync
```

## 常见问题

### Q: 启动失败？

A: 检查端口是否被占用：
```bash
lsof -i :8000
```

### Q: Token 失效？

A: 进入管理后台刷新 Token，或添加新 Token

### Q: API 调用失败？

A: 
1. 检查 API Key 是否正确
2. 查看日志排查错误
3. 确认 Token 池有可用 Token

### Q: 性能不够？

A:
1. 增加 Worker 数量
2. 使用 Redis 存储
3. 添加更多 Token
4. 启用真实上下文节省 Token

## 下一步

- 阅读 FEATURES.md 了解所有功能
- 查看 README.md 了解详细配置
- 根据需求启用高级功能
- 生产环境部署优化
