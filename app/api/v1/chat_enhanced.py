"""
Enhanced Chat API with Real Context Management
整合 Tomiya233/grok2api_new 的真实上下文功能
"""

import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse

from app.api.v1.chat import (
    ChatCompletionRequest,
    MessageItem,
    chat_completions as original_chat_completions,
)
from app.services.context.conversation_manager import ConversationManager
from app.services.grok.services.chat import ChatService
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


def extract_new_messages(
    messages: List[MessageItem], context
) -> List[Dict[str, Any]]:
    """
    提取新消息（续接对话时只发送新消息）
    
    Args:
        messages: 完整消息列表
        context: 会话上下文
        
    Returns:
        新消息列表
    """
    if not context:
        return [msg.model_dump() for msg in messages]
    
    # 根据 message_count 判断哪些是新消息
    # 假设前 N 条是历史，后面的是新消息
    history_count = context.message_count
    
    # 简单实现：只取最后一条用户消息
    # 更复杂的实现需要根据实际消息历史匹配
    new_messages = []
    for msg in reversed(messages):
        if msg.role == "user":
            new_messages.insert(0, msg.model_dump())
            break
    
    return new_messages


@router_enhanced.post("/v1/chat/completions")
async def chat_completions_enhanced(request_data: ChatCompletionRequest, req: Request):
    """
    增强的对话补全 API
    
    使用 Tomiya233/grok2api_new 的真实上下文管理：
    1. 自动识别会话（通过消息历史哈希）
    2. 续接对话时只发送新消息
    3. 保存会话上下文供下次使用
    """
    # 检查是否启用真实上下文
    context_enabled = get_config("context.enabled", False)
    
    if not context_enabled:
        # 未启用，使用原版
        logger.debug("[Enhanced Chat] Context disabled, using original implementation")
        return await original_chat_completions(request_data, req)
    
    # 启用了真实上下文
    await init_context_manager()
    
    # 1. 尝试获取或识别会话
    conversation_id = getattr(request_data, 'conversation_id', None)
    context = None
    
    if conversation_id:
        # 显式提供了会话ID
        context = await conv_manager.get_conversation(conversation_id)
        if context:
            logger.info(f"[Enhanced Chat] Found existing conversation: {conversation_id}")
    
    if not context and request_data.messages and len(request_data.messages) > 1:
        # 尝试通过消息历史自动识别
        messages_dict = [msg.model_dump() for msg in request_data.messages]
        auto_conv_id = await conv_manager.find_conversation_by_history(messages_dict)
        
        if auto_conv_id:
            context = await conv_manager.get_conversation(auto_conv_id)
            conversation_id = auto_conv_id
            logger.info(f"[Enhanced Chat] Auto-detected conversation: {conversation_id}")
    
    # 2. 如果是新对话，分配会话ID
    if not conversation_id:
        conversation_id = f"conv-{uuid.uuid4().hex[:24]}"
        logger.info(f"[Enhanced Chat] New conversation: {conversation_id}")
    
    # 3. 准备消息
    if context:
        # 续接对话：只发送新消息
        messages_to_send = extract_new_messages(request_data.messages, context)
        logger.info(f"[Enhanced Chat] Continuing conversation, sending {len(messages_to_send)} new messages")
    else:
        # 新对话：发送所有消息
        messages_to_send = [msg.model_dump() for msg in request_data.messages]
        logger.info(f"[Enhanced Chat] New conversation, sending {len(messages_to_send)} messages")
    
    # 4. 调用原版 ChatService（它会处理实际的 Grok API 调用）
    # 注意：这里我们需要修改 request_data.messages
    original_messages = request_data.messages
    request_data.messages = [MessageItem(**msg) for msg in messages_to_send]
    
    try:
        # 调用原版实现
        result = await ChatService.completions(
            model=request_data.model,
            messages=messages_to_send,
            stream=request_data.stream,
            reasoning_effort=request_data.reasoning_effort,
            temperature=request_data.temperature,
            top_p=request_data.top_p,
            tools=request_data.tools,
            tool_choice=request_data.tool_choice,
            parallel_tool_calls=request_data.parallel_tool_calls,
        )
        
        # 5. 保存或更新会话上下文
        # TODO: 从 result 中提取 grok_conversation_id 和 grok_response_id
        # 这需要修改 ChatService 返回这些信息
        
        # 暂时使用消息历史哈希保存
        if not context:
            # 新对话，创建上下文
            await conv_manager.create_conversation(
                openai_conversation_id=conversation_id,
                grok_conversation_id="",  # TODO: 从 result 提取
                grok_response_id="",  # TODO: 从 result 提取
                token="",  # TODO: 从 token_manager 获取
                messages=original_messages,
            )
            logger.info(f"[Enhanced Chat] Created new conversation context: {conversation_id}")
        else:
            # 续接对话，更新上下文
            await conv_manager.update_conversation(
                conversation_id=conversation_id,
                grok_response_id="",  # TODO: 从 result 提取
                messages=original_messages,
            )
            logger.info(f"[Enhanced Chat] Updated conversation context: {conversation_id}")
        
        # 6. 返回结果
        if isinstance(result, dict):
            # 非流式响应，添加 conversation_id
            result['conversation_id'] = conversation_id
            return JSONResponse(content=result)
        else:
            # 流式响应
            return StreamingResponse(
                result,
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Conversation-ID": conversation_id,
                },
            )
    
    except Exception as e:
        logger.error(f"[Enhanced Chat] Error: {e}")
        # 恢复原始消息
        request_data.messages = original_messages
        raise


# 导出增强路由
__all__ = ["router_enhanced", "init_context_manager"]
