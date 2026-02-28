"""
Enhanced Chat API with Real Context Management
整合 DeVibe-one 的真实上下文功能
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse

from app.api.v1.chat import (
    router as original_router,
    ChatCompletionRequest,
    chat_completions as original_chat_completions
)
from app.services.context.conversation_manager import ConversationManager
from app.core.config import get_config
from app.core.logger import logger

# 创建增强路由
router_enhanced = APIRouter()

# 初始化上下文管理器
conv_manager = ConversationManager()


async def init_context_manager():
    """初始化上下文管理器"""
    if not conv_manager.initialized:
        await conv_manager.init()
        logger.info("[Enhanced Chat] Context manager initialized")


@router_enhanced.post("/v1/chat/completions")
async def chat_completions_enhanced(request_data: ChatCompletionRequest, req: Request):
    """
    增强的对话补全 API
    
    如果启用了真实上下文 (context.enabled=true)，则使用 DeVibe-one 的上下文管理
    否则回退到原版实现
    """
    # 检查是否启用真实上下文
    context_enabled = get_config("context.enabled", False)
    
    if not context_enabled:
        # 未启用，使用原版
        return await original_chat_completions(request_data, req)
    
    # 启用了真实上下文
    await init_context_manager()
    
    # 尝试自动识别会话
    conversation_id = getattr(request_data, 'conversation_id', None)
    
    if not conversation_id and request_data.messages:
        # 尝试通过消息历史自动识别
        conversation_id = await conv_manager.find_conversation_by_history(
            [msg.dict() for msg in request_data.messages]
        )
        
        if conversation_id:
            logger.info(f"[Enhanced Chat] Auto-detected conversation: {conversation_id}")
    
    # TODO: 这里需要调用 Grok API 并使用真实的 conversationId
    # 当前先回退到原版实现
    # 完整实现需要：
    # 1. 如果有 conversation_id，从 conv_manager 获取 grok_conversation_id 和 grok_response_id
    # 2. 调用 Grok API 续接对话（只发送新消息）
    # 3. 更新 conv_manager 中的上下文
    # 4. 如果是新对话，创建新的上下文记录
    
    logger.warning("[Enhanced Chat] Real context enabled but not fully implemented, falling back to original")
    return await original_chat_completions(request_data, req)


# 导出增强路由
__all__ = ["router_enhanced", "init_context_manager"]
