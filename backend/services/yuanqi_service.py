import os
import httpx
import json
from typing import Optional, Dict, Any, AsyncGenerator


class YuanqiService:
    """腾讯元器API服务"""

    def __init__(
        self,
        api_key: str,
        assistant_id: str,
        base_url: str = "https://yuanqi.tencent.com/openapi/v1/agent/chat/completions"
    ):
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.base_url = base_url
        self.timeout = 120.0

    def _build_payload(self, query: str, user_id: str, stream: bool) -> Dict[str, Any]:
        return {
            "assistant_id": self.assistant_id,
            "user_id": user_id,
            "stream": stream,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        }
                    ]
                }
            ]
        }

    @staticmethod
    def _extract_message_text(message_content: Any) -> str:
        """兼容元器不同 content 结构：string / list / object"""
        if isinstance(message_content, str):
            return message_content

        if isinstance(message_content, list):
            parts: list[str] = []
            for item in message_content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(item.get("text", ""))
                    elif "text" in item:
                        parts.append(str(item.get("text", "")))
                elif isinstance(item, str):
                    parts.append(item)
            return "".join(parts)

        if isinstance(message_content, dict):
            if "text" in message_content:
                return str(message_content.get("text", ""))

        return ""

    @staticmethod
    def _extract_from_message_obj(message_obj: Dict[str, Any]) -> str:
        # 优先使用 content；若为空，再回退常见字段
        text = YuanqiService._extract_message_text(message_obj.get("content"))
        if text:
            return text

        for key in ("output", "text", "reasoning_content"):
            value = message_obj.get(key)
            if isinstance(value, str) and value.strip():
                return value
        return ""

    async def stream_chat(
        self,
        query: str,
        user_id: str = "anonymous"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式对话接口"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = self._build_payload(query, user_id, stream=True)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    self.base_url,
                    json=payload,
                    headers=headers
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue

                        # 处理SSE格式: data: {JSON}
                        json_data = line[6:].strip()
                        if json_data and json_data != "[DONE]":
                            try:
                                yield json.loads(json_data)
                            except json.JSONDecodeError:
                                continue
            except httpx.HTTPStatusError as e:
                error_detail = await e.response.aread()
                raise ConnectionError(f"元器API错误 {e.response.status_code}: {error_detail.decode()}") from e
            except httpx.TimeoutException as e:
                raise ConnectionError("元器流式响应超时，请稍后重试") from e
            except Exception as e:
                raise ConnectionError(f"请求失败: {str(e)}") from e

    async def chat(
        self,
        query: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """非流式对话接口（严格按元器文档 stream=false）"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = self._build_payload(query, user_id, stream=False)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                full_content = ""
                choices = data.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    full_content = self._extract_from_message_obj(message)

                if not full_content:
                    # 兼容部分工作流返回结构
                    for key in ("output", "text", "reasoning_content"):
                        value = data.get(key)
                        if isinstance(value, str) and value.strip():
                            full_content = value
                            break

                return {
                    "response": full_content,
                    "response_id": data.get("id"),
                    "usage": data.get("usage", {})
                }
            except httpx.HTTPStatusError as e:
                raise ConnectionError(f"元器API错误 {e.response.status_code}: {e.response.text}") from e
            except httpx.TimeoutException as e:
                raise ConnectionError("元器响应超时，请稍后重试") from e
            except Exception as e:
                raise ConnectionError(f"请求失败: {str(e)}") from e

    async def chat_raw(
        self,
        query: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """返回元器原始响应（用于调试字段结构）"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = self._build_payload(query, user_id, stream=False)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise ConnectionError(f"元器API错误 {e.response.status_code}: {e.response.text}") from e
            except httpx.TimeoutException as e:
                raise ConnectionError("元器响应超时，请稍后重试") from e
            except Exception as e:
                raise ConnectionError(f"请求失败: {str(e)}") from e

    async def get_legal_advice(
        self,
        query: str,
        context: Optional[str] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """获取法律建议（聚合元器响应）"""
        # 构建完整法律咨询query
        full_query = query
        if context:
            full_query = f"{query}\n\n附加上下文: {context}"

        result = await self.chat(full_query, user_id)

        return {
            "query": query,
            "response": result.get("response", ""),
            "confidence": 0.85,  # TODO: 根据元器返回内容计算置信度
            "references": [],  # TODO: 解析法律条文引用
            "response_id": result.get("response_id")
        }

    async def generate_lawsuit_fields(
        self,
        case_facts: str,
        legal_advice: str,
        evidence_list: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """根据案情和法律建议，智能生成起诉状的各个字段"""
        prompt = f"""你是一名专业的中国民事诉讼文书律师助理。请根据以下信息，生成一份完整的民事起诉状所需的所有字段。

请严格按照以下 JSON 格式返回，不要包含其他内容：

{{
  "claims": "诉讼请求，每行一项，用\\n分隔",
  "facts_and_reasons": "事实与理由的完整描述",
  "legal_basis": "相关法律依据（法条）",
  "evidence_list": "证据清单，每行一项，用\\n分隔"
}}

【案情描述】
{case_facts}

【法律分析建议】
{legal_advice}

【证据材料】
{evidence_list or "无"}

请生成标准格式的起诉状字段，确保：
1. 诉讼请求明确、具体、可执行
2. 事实与理由逻辑清晰、条理分明
3. 法律依据准确引用相关法条
4. 证据清单与案情匹配"""

        result = await self.chat(prompt, user_id)
        response_text = result.get("response", "")

        # 尝试解析 JSON
        import json
        import re
        
        try:
            # 提取 JSON 部分
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                fields = json.loads(json_match.group())
                return {
                    "success": True,
                    "fields": fields,
                    "raw_response": response_text
                }
            else:
                return {
                    "success": False,
                    "error": "无法解析元器返回的 JSON",
                    "raw_response": response_text
                }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "JSON 解析失败",
                "raw_response": response_text
            }