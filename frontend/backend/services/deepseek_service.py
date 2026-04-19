"""
DeepSeek服务
实现与DeepSeek API的连接和交互
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime


class DeepSeekService:
    """DeepSeek服务类"""

    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured in environment variables")

    def generate_lawsuit(self, case_info: Dict[str, Any], legal_provisions: str,
                       template_content: str, user_requirements: str) -> Dict[str, Any]:
        """
        生成诉状

        Args:
            case_info: 案件信息（用户输入的案情）
            legal_provisions: 法律条文（来自元器API）
            template_content: 诉状模板内容
            user_requirements: 用户具体诉求

        Returns:
            包含生成结果的字典
        """
        try:
            # 构建系统提示
            system_prompt = f"""
你是一名专业的法律文书撰写专家。请根据以下信息生成符合法律规范的诉状：

1. 案件信息：
{case_info.get('case_info', '')}

2. 法律依据：
{legal_provisions}

3. 用户诉求：
{user_requirements}

4. 诉状模板要求：
请按照以下模板格式生成诉状：
{template_content}

请确保：
- 使用正式的法律文书语言
- 包含完整的诉讼请求
- 事实与理由部分逻辑清晰
- 法律依据引用准确
- 格式符合法院要求
"""

            # 构建请求 payload
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": "请根据上述信息生成完整的诉状"
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }

            # 发送请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
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
                error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '诉状生成失败'
            }

    def refine_document(self, original_content: str, template: str, style: str = "legal") -> Dict[str, Any]:
        """
        文书润色

        Args:
            original_content: 原始内容
            template: 模板要求
            style: 润色风格

        Returns:
            包含润色结果的字典
        """
        try:
            system_prompt = f"""
你是一名专业的法律文书编辑。请根据以下要求对内容进行润色：

1. 原始内容：
{original_content}

2. 模板要求：
{template}

3. 润色风格：
请使用{style}风格进行润色，确保：
- 语言正式、专业
- 逻辑清晰、条理分明
- 符合法律文书规范
- 保留原始事实和诉求
"""

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": "请根据上述要求对内容进行润色和优化"
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 3000
            }

            response = requests.post(
                self.api_url,
                headers=self.headers,
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
                error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '文书润色失败'
            }

    def summarize_legal_info(self, legal_text: str) -> Dict[str, Any]:
        """
        法律条文摘要

        Args:
            legal_text: 法律条文内容

        Returns:
            包含摘要结果的字典
        """
        try:
            system_prompt = f"""
你是一名法律专家。请对以下法律条文进行摘要：

法律条文：
{legal_text}

请生成：
1. 核心要点
2. 适用条件
3. 相关责任
4. 法律后果

确保摘要准确、简洁、专业。
"""

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": "请对上述法律条文进行摘要"
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }

            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

                return {
                    'success': True,
                    'summary': content,
                    'usage': result.get('usage', {}),
                    'model': result.get('model', '')
                }
            else:
                error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '法律条文摘要失败'
            }


# 服务实例
deepseek_service = DeepSeekService()