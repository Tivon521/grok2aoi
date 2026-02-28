#!/bin/bash

echo "==================================="
echo "Grok2API Ultimate Edition v1.0.0"
echo "==================================="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo "安装 Docker:"
    echo "  curl -fsSL https://get.docker.com | sh"
    exit 1
fi

echo "✅ Docker 已安装"

# 检查 docker compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

echo "✅ Docker Compose 已安装"
echo ""

# 创建数据目录
mkdir -p data logs
echo "✅ 创建数据目录"

# 启动服务
echo ""
echo "启动服务..."
docker compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "✅ 安装成功！"
    echo "==================================="
    echo ""
    echo "访问地址："
    echo "  管理后台: http://localhost:8000/admin"
    echo "  API 地址: http://localhost:8000/v1"
    echo ""
    echo "默认密码: grok2api"
    echo ""
    echo "查看日志:"
    echo "  docker compose logs -f"
    echo ""
    echo "停止服务:"
    echo "  docker compose down"
    echo ""
else
    echo "❌ 启动失败，请查看错误信息"
    exit 1
fi
