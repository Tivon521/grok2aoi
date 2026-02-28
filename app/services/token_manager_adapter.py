"""Token Manager Adapter - 适配 chenyme 的 token 系统"""

from app.core.storage import StorageFactory
from app.core.logger import logger
from typing import Set, Optional
import random
import json
from pathlib import Path


class TokenManagerAdapter:
    """简化的 Token 管理器"""
    
    def __init__(self):
        self.tokens = []
        self._load_tokens()
    
    def _load_tokens(self):
        """从 token.json 加载 Token"""
        token_file = Path("data/token.json")
        if token_file.exists():
            try:
                with open(token_file, "r") as f:
                    data = json.load(f)
                    # 获取 ssoBasic 池中的所有 active token
                    if "ssoBasic" in data:
                        self.tokens = [
                            t["token"] for t in data["ssoBasic"]
                            if t.get("status") == "active" and t.get("quota", 0) > 0
                        ]
                logger.info(f"[TokenManager] 加载了 {len(self.tokens)} 个可用 Token")
            except Exception as e:
                logger.error(f"[TokenManager] 加载 Token 失败: {e}")
    
    async def get_token(self, exclude: Set[str] = None) -> str:
        """获取一个可用的 token"""
        if not self.tokens:
            self._load_tokens()
        
        if not self.tokens:
            raise Exception("没有可用的 Token")
        
        # 过滤掉已使用的 token
        available = [t for t in self.tokens if not exclude or t not in exclude]
        
        if not available:
            raise Exception("所有 Token 都已尝试过")
        
        # 随机选择一个
        return random.choice(available)
    
    async def record_success(self, token: str):
        """记录成功"""
        pass
    
    async def record_failure(self, token: str, reason: str = "normal", has_quota: bool = True):
        """记录失败"""
        logger.warning(f"[TokenManager] Token 失败: {reason}, has_quota={has_quota}")


# 全局实例
token_manager = TokenManagerAdapter()
