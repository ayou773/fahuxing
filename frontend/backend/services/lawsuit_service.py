"""
诉状生成服务
整合元器API和DeepSeek API生成诉状
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .deepseek_service import deepseek_service
from .pdf_generator import pdf_generator


class LawsuitService:
    """诉状生成服务类"""

    def __init__(self):
        self.yuanqi_api_key = os.getenv('YUANQI_API_KEY')
        self.yuanqi_assistant_id = os.getenv('YUANQI_ASSISTANT_ID')
        self.yuanqi_api_url = "https://api.yuanqi.ai/v1/chat/completions"

        if not self.yuanqi_api_key or not self.yuanqi_assistant_id:
            raise ValueError("YUANQI_API_KEY and YUANQI_ASSISTANT_ID must be configured")

    def generate_lawsuit(self, case_info: Dict[str, Any], template_content: str) -> Dict[str, Any]:
        """
        生成诉状

        Args:
            case_info: 案件信息
            template_content: 诉状模板内容

        Returns:
            包含生成结果的字典
        """
        try:
            # 1. 调用元器API获取法律条文
            legal_provisions = self._get_legal_provisions(case_info)

            if not legal_provisions.get('success', False):
                return {
                    'success': False,
                    'error': legal_provisions.get('error', '获取法律条文失败'),
                    'message': '诉状生成失败：无法获取法律条文'
                }

            # 2. 使用DeepSeek生成诉状
            deepseek_result = deepseek_service.generate_lawsuit(
                case_info=case_info,
                legal_provisions=legal_provisions.get('content', ''),
                template_content=template_content,
                user_requirements=case_info.get('user_requirements', '')
            )

            if not deepseek_result.get('success', False):
                return {
                    'success': False,
                    'error': deepseek_result.get('error', 'DeepSeek生成失败'),
                    'message': '诉状生成失败：DeepSeek处理失败'
                }

            # 3. 生成PDF
            pdf_result = pdf_generator.generate_lawsuit_pdf(
                lawsuit_content=deepseek_result.get('content', ''),
                case_info=case_info
            )

            if not pdf_result.get('success', False):
                return {
                    'success': False,
                    'error': pdf_result.get('error', 'PDF生成失败'),
                    'message': '诉状生成失败：PDF生成失败'
                }

            return {
                'success': True,
                'lawsuit_content': deepseek_result.get('content', ''),
                'pdf_path': pdf_result.get('file_path', ''),
                'pdf_name': pdf_result.get('file_name', ''),
                'legal_provisions': legal_provisions.get('content', ''),
                'message': '诉状生成成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '诉状生成过程中发生错误'
            }

    def _get_legal_provisions(self, case_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用元器API获取法律条文

        Args:
            case_info: 案件信息

        Returns:
            包含法律条文结果的字典
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.yuanqi_api_key}",
                "Content-Type": "application/json"
            }

            # 构建请求 payload
            payload = {
                "assistant_id": self.yuanqi_assistant_id,
                "messages": [
                    {
                        "role": "user",
                        "content": f"""
请根据以下案件信息查找相关的法律条文：

案件信息：
{case_info.get('case_info', '')}

请返回：
1. 相关的法律条文
2. 适用条件
3. 相关责任
4. 法律后果

请以JSON格式返回结果。
"""
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }

            # 发送请求
            response = requests.post(
                self.yuanqi_api_url,
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

                return {
                    'success': True,
                    'content': content,
                    'usage': result.get('usage', {}),
                    'model': result.get('model', '')
                }
            else:
                error_msg = f"元器API error: {response.status_code} - {response.text}"
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '获取法律条文失败'
            }

    def generate_calculation_report(self, calculation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成计算报告

        Args:
            calculation_data: 计算数据

        Returns:
            包含生成结果的字典
        """
        try:
            # 生成计算报告PDF
            pdf_result = pdf_generator.generate_calculation_report(
                calculation_results=calculation_data
            )

            if not pdf_result.get('success', False):
                return {
                    'success': False,
                    'error': pdf_result.get('error', 'PDF生成失败'),
                    'message': '计算报告生成失败'
                }

            return {
                'success': True,
                'pdf_path': pdf_result.get('file_path', ''),
                'pdf_name': pdf_result.get('file_name', ''),
                'message': '计算报告生成成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '计算报告生成失败'
            }


# 服务实例
lawsuit_service = LawsuitService()