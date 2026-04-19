"""
咨询记录路由
处理咨询记录相关的API请求
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime

from ..services.lawsuit_service import lawsuit_service


router = APIRouter()


@router.post("/consultations/{consultation_id}/lawsuit")
async def generate_lawsuit_from_consultation(consultation_id: str, data: Dict[str, Any]):
    """
    从咨询记录生成诉状

    Args:
        consultation_id: 咨询记录ID
        data: 案件信息字典
            case_info: 案件详情
            plaintiff: 原告信息
            defendant: 被告信息
            case_cause: 案由
            requests: 诉讼请求列表
            evidence: 证据清单
            user_requirements: 用户诉求

    Returns:
        诉状生成结果，包含PDF文件路径
    """
    try:
        # 检查必要参数
        required_fields = ['case_info', 'plaintiff', 'defendant', 'case_cause', 'requests', 'evidence']
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # 生成诉状
        result = lawsuit_service.generate_lawsuit(
            case_info=data,
            template_content=""  # 使用默认模板
        )

        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('message', 'Lawsuit generation failed'))

        return {
            'success': True,
            'pdf_path': result.get('pdf_path', ''),
            'pdf_name': result.get('pdf_name', ''),
            'message': '诉状生成成功'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consultations/{consultation_id}")
async def get_consultation(consultation_id: str):
    """
    获取咨询记录

    Args:
        consultation_id: 咨询记录ID

    Returns:
        咨询记录详情
    """
    try:
        # 这里应该从数据库或存储中获取咨询记录
        # 目前返回模拟数据
        mock_consultation = {
            "id": consultation_id,
            "query": "劳动纠纷咨询",
            "created_at": datetime.now().isoformat(),
            "case_info": "员工与公司之间的劳动纠纷",
            "plaintiff": "张三",
            "defendant": "某科技公司",
            "case_cause": "劳动报酬纠纷"
        }

        return {
            'success': True,
            'consultation': mock_consultation
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))