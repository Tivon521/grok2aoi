"""
Auto Register API
整合 TQZHR 的自动注册功能
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.core.auth import verify_api_key
from app.core.config import get_config
from app.core.logger import logger
from app.services.register.manager import AutoRegisterManager

router = APIRouter()


class AutoRegisterRequest(BaseModel):
    """自动注册请求"""
    count: Optional[int] = None
    concurrency: Optional[int] = None


@router.post("/api/v1/admin/auto-register", dependencies=[Depends(verify_api_key)])
async def auto_register_tokens(data: AutoRegisterRequest):
    """
    自动注册 Token
    
    需要配置：
    - register.enabled = true
    - register.worker_domain
    - register.email_domain
    - register.solver_url 或 register.yescaptcha_client_key
    """
    # 检查是否启用
    if not get_config("register.enabled", False):
        return {
            "success": False,
            "message": "Auto register is not enabled. Set register.enabled=true in config."
        }
    
    # 获取参数
    count = data.count or int(get_config("register.default_count", 100))
    concurrency = data.concurrency or int(get_config("register.default_concurrency", 10))
    
    logger.info(f"[Auto Register] Starting: count={count}, concurrency={concurrency}")
    
    try:
        # 创建管理器
        manager = AutoRegisterManager()
        
        # 执行注册
        result = await manager.register_batch(count=count, concurrency=concurrency)
        
        return {
            "success": True,
            "message": f"Registered {result['success']} tokens successfully",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"[Auto Register] Failed: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/api/v1/admin/auto-register/status", dependencies=[Depends(verify_api_key)])
async def auto_register_status():
    """获取自动注册状态"""
    enabled = get_config("register.enabled", False)
    
    if not enabled:
        return {
            "enabled": False,
            "message": "Auto register is disabled"
        }
    
    return {
        "enabled": True,
        "config": {
            "worker_domain": get_config("register.worker_domain"),
            "email_domain": get_config("register.email_domain"),
            "solver_url": get_config("register.solver_url"),
            "default_count": get_config("register.default_count", 100),
            "default_concurrency": get_config("register.default_concurrency", 10),
            "has_yescaptcha": bool(get_config("register.yescaptcha_client_key"))
        }
    }


__all__ = ["router"]
