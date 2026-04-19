"""
诉状生成路由
处理诉状生成相关的API请求
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Dict, Any, Optional
from datetime import datetime

from ..services.lawsuit_service import lawsuit_service
from ..services.pdf_generator import pdf_generator


router = APIRouter()


@router.post("/generate/lawsuit")
async def generate_lawsuit(data: Dict[str, Any], template_file: Optional[UploadFile] = File(None)):
    """
    生成诉状

    Args:
        data: 案件信息字典
            case_info: 案件详情
            plaintiff: 原告信息
            defendant: 被告信息
            case_cause: 案由
            requests: 诉讼请求列表
            evidence: 证据清单
            user_requirements: 用户诉求
        template_file: 诉状模板文件（可选）

    Returns:
        诉状生成结果，包含PDF文件路径
    """
    try:
        # 检查必要参数
        required_fields = ['case_info', 'plaintiff', 'defendant', 'case_cause', 'requests', 'evidence']
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # 处理模板文件
        template_content = ""
        if template_file:
            template_content = await template_file.read().decode('utf-8')
        else:
            # 如果没有提供模板文件，使用默认模板
            template_content = """
请按照以下格式生成诉状：

民事起诉状

原告：[原告信息]

被告：[被告信息]

案由：[案由]

诉讼请求：
1. [请求1]
2. [请求2]
...

事实与理由：
[事实与理由详细内容]

证据清单：
1. [证据1]
2. [证据2]
...

此致
XX人民法院

起诉人：[原告姓名]
[日期]
"""

        # 生成诉状
        result = lawsuit_service.generate_lawsuit(
            case_info=data,
            template_content=template_content
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


@router.post("/generate/calculation-report")
async def generate_calculation_report(data: Dict[str, Any]):
    """
    生成计算报告

    Args:
        data: 计算数据字典

    Returns:
        计算报告生成结果，包含PDF文件路径
    """
    try:
        result = lawsuit_service.generate_calculation_report(
            calculation_data=data
        )

        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('message', 'Calculation report generation failed'))

        return {
            'success': True,
            'pdf_path': result.get('pdf_path', ''),
            'pdf_name': result.get('pdf_name', ''),
            'message': '计算报告生成成功'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/pdf")
async def export_pdf(content: str, filename: str, template: Optional[str] = None):
    """
    导出内容为PDF

    Args:
        content: 要导出的内容
        filename: 文件名
        template: 模板名称（可选）

    Returns:
        PDF导出结果
    """
    try:
        if template:
            result = pdf_generator.generate_template_pdf(
                template_name=template,
                data={'content': content},
                output_filename=filename
            )
        else:
            # 简单的文本导出
            result = pdf_generator.generate_lawsuit_pdf(
                lawsuit_content=content,
                case_info={'title': filename},
                output_filename=filename
            )

        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('message', 'PDF export failed'))

        return {
            'success': True,
            'pdf_path': result.get('file_path', ''),
            'pdf_name': result.get('file_name', ''),
            'message': 'PDF导出成功'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))