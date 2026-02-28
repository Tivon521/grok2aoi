"""Tomiya233 的聊天 API - 简化版"""

import time
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import StreamingResponse

from app.models.openai_models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseMessage,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
)
from app.services.grok_client import GrokClient
from app.core.auth import verify_api_key
from app.core.logger import logger

router = APIRouter()


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    raw_request: Request,
    token: str = Depends(verify_api_key)
):
    """聊天补全接口 - 支持真实上下文"""
    
    start_time = time.time()
    request_id = f"req-{uuid.uuid4().hex[:16]}"
    
    try:
        conv_id = (request.conversation_id or "").strip() or None
        
        logger.info(
            f"[ChatAPI] 请求: model={request.model}, stream={request.stream}, conv_id={conv_id}"
        )
        
        # 调用 Grok 客户端
        result, openai_conv_id, _, _ = await GrokClient.chat(
            messages=[msg.model_dump() for msg in request.messages],
            model=request.model,
            stream=request.stream,
            conversation_id=conv_id,
            thinking=request.thinking,
        )
        
        if request.stream:
            # 流式响应
            async def stream_wrapper():
                try:
                    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
                    created = int(time.time())
                    
                    # 第一个块包含会话ID
                    first_chunk = ChatCompletionChunk(
                        id=chunk_id,
                        created=created,
                        model=request.model,
                        choices=[
                            ChatCompletionChunkChoice(
                                index=0,
                                delta=ChatCompletionChunkDelta(role="assistant"),
                                finish_reason=None,
                            )
                        ],
                        conversation_id=openai_conv_id,
                    )
                    yield f"data: {first_chunk.model_dump_json()}\n\n"
                    
                    # 流式内容
                    async for text in result:
                        chunk = ChatCompletionChunk(
                            id=chunk_id,
                            created=created,
                            model=request.model,
                            choices=[
                                ChatCompletionChunkChoice(
                                    index=0,
                                    delta=ChatCompletionChunkDelta(content=text),
                                    finish_reason=None,
                                )
                            ],
                        )
                        yield f"data: {chunk.model_dump_json()}\n\n"
                    
                    # 结束块
                    end_chunk = ChatCompletionChunk(
                        id=chunk_id,
                        created=created,
                        model=request.model,
                        choices=[
                            ChatCompletionChunkChoice(
                                index=0,
                                delta=ChatCompletionChunkDelta(),
                                finish_reason="stop",
                            )
                        ],
                    )
                    yield f"data: {end_chunk.model_dump_json()}\n\n"
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    logger.error(f"[ChatAPI] 流式错误: {e}")
                    error_chunk = ChatCompletionChunk(
                        id=f"chatcmpl-{uuid.uuid4().hex[:24]}",
                        created=int(time.time()),
                        model=request.model,
                        choices=[
                            ChatCompletionChunkChoice(
                                index=0,
                                delta=ChatCompletionChunkDelta(content=f"Error: {str(e)}"),
                                finish_reason="error",
                            )
                        ],
                    )
                    yield f"data: {error_chunk.model_dump_json()}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                stream_wrapper(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Request-ID": request_id,
                }
            )
        else:
            # 非流式响应
            response = ChatCompletionResponse(
                id=f"chatcmpl-{uuid.uuid4().hex[:24]}",
                created=int(time.time()),
                model=request.model,
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=ChatCompletionResponseMessage(
                            role="assistant",
                            content=result
                        ),
                        finish_reason="stop"
                    )
                ],
                usage={
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                conversation_id=openai_conv_id
            )
            
            logger.info(f"[ChatAPI] 完成: conv_id={openai_conv_id}")
            return response
            
    except Exception as e:
        logger.error(f"[ChatAPI] 错误: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": str(e),
                    "type": "internal_error",
                    "code": "chat_error"
                }
            }
        )
