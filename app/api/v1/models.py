"""
Models API 路由
"""

from fastapi import APIRouter

from app.services.grok.services.model import ModelService


router = APIRouter(tags=["Models"])


@router.get("/models")
async def list_models():
    """OpenAI 兼容 models 列表接口"""
    data = [
        {
            "id": m.model_id,
            "object": "model",
            "created": 0,
            "owned_by": "grok2api@chenyme",
        }
        for m in ModelService.list()
    ]
    return {"object": "list", "data": data}


__all__ = ["router"]


def resolve_model(model_id: str):
    """解析模型ID - 简化版本，直接返回原始ID"""
    # 简化实现：直接返回原始模型ID
    return model_id, "MODEL_MODE_AUTO", model_id
