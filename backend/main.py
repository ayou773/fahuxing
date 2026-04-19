import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import init_db, AsyncSessionLocal
from models.consultation import Consultation
from services.yuanqi_service import YuanqiService
from services.document_service import DocumentService
from services.calculator_service import CalculatorService
from repositories.consultation_repo import ConsultationRepository
from routers.lawsuit import router as lawsuit_router

app = FastAPI(title="法护星法律助手", version="1.0.0")
BACKEND_BUILD = "2026-04-17-raw-fallback-v2"

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(lawsuit_router)

# 初始化服务
YUANQI_API_KEY = os.getenv("YUANQI_API_KEY")
YUANQI_ASSISTANT_ID = os.getenv("YUANQI_ASSISTANT_ID")

yuanqi_service = None
if YUANQI_API_KEY and YUANQI_ASSISTANT_ID:
    yuanqi_service = YuanqiService(
        api_key=YUANQI_API_KEY,
        assistant_id=YUANQI_ASSISTANT_ID
    )
document_service = DocumentService()
calculator_service = CalculatorService()


class ConsultationRequest(BaseModel):
    query: str
    context: str | None = None
    user_id: str = "anonymous"


@app.get("/health")
async def health_check():
    return {"status": "online", "service": "legal-assistant", "build": BACKEND_BUILD}


# 依赖项：获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.post("/consultation")
async def create_consultation(
    request: ConsultationRequest,
    db: AsyncSession = Depends(get_db)
):
    if not yuanqi_service:
        raise HTTPException(status_code=503, detail="元器服务未配置，请检查 YUANQI_API_KEY 和 YUANQI_ASSISTANT_ID")

    try:
        advice = await yuanqi_service.get_legal_advice(
            request.query,
            request.context,
            request.user_id
        )
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=f"元器调用失败: {str(e)}") from e

    # 保存咨询记录
    consultation = Consultation(
        user_id=request.user_id,
        query=request.query,
        context=request.context,
        response=advice.get("response", ""),
        case_type="civil"
    )
    consultation = await ConsultationRepository.save(db, consultation)
    await db.commit()

    return {
        **advice,
        "consultation_id": str(consultation.id)
    }


class ChecklistRequest(BaseModel):
    incident: str
    context: str | None = None
    user_id: str = "anonymous"


def _extract_text_from_raw(raw: dict) -> str:
    """从元器原始响应中尽可能提取文本内容。"""
    choices = raw.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                elif isinstance(item, str):
                    parts.append(item)
            text = "".join(parts).strip()
            if text:
                return text

        for key in ("output", "text", "reasoning_content"):
            value = message.get(key)
            if isinstance(value, str) and value.strip():
                return value

    for key in ("output", "text", "reasoning_content"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value

    return ""


class OvertimeCalcRequest(BaseModel):
    monthly_salary: float
    overtime_hours_weekday: float = 0.0
    overtime_hours_restday: float = 0.0
    overtime_hours_holiday: float = 0.0


class CompensationCalcRequest(BaseModel):
    monthly_salary: float
    worked_years: float


@app.post("/debug/yuanqi/raw")
async def debug_yuanqi_raw(request: ChecklistRequest):
    if not yuanqi_service:
        raise HTTPException(status_code=503, detail="元器服务未配置，请检查 YUANQI_API_KEY 和 YUANQI_ASSISTANT_ID")

    debug_prompt = f"""你是一名基层纠纷维权顾问。请根据用户描述生成“维权行动清单”。

用户描述：
{request.incident}

附加信息：
{request.context or "无"}
"""
    try:
        raw = await yuanqi_service.chat_raw(debug_prompt, request.user_id)
        return raw
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=f"元器调用失败: {str(e)}") from e


@app.post("/rights/checklist")
async def generate_rights_checklist(request: ChecklistRequest):
    if not yuanqi_service:
        raise HTTPException(status_code=503, detail="元器服务未配置，请检查 YUANQI_API_KEY 和 YUANQI_ASSISTANT_ID")
    prompt = f"""你是一名基层纠纷维权顾问。请根据用户描述生成“维权行动清单”。

输出要求：
1. 使用 Markdown 二级标题
2. 必须包含四部分：立即行动（24小时内）/ 短期行动（7天内）/ 中期行动（30天内）/ 风险提醒
3. 每一步写清“目的 + 操作动作 + 预期结果”
4. 用词务实，避免空泛表述

用户描述：
{request.incident}

附加信息：
{request.context or "无"}
"""
    try:
        result = await yuanqi_service.chat(prompt, request.user_id)
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=f"元器调用失败: {str(e)}") from e
    checklist = (result.get("response", "") or "").strip()

    # 方法切换：当主解析为空时，回退到原始响应提取，避免前端拿到空字符串
    if not checklist:
        try:
            raw = await yuanqi_service.chat_raw(prompt, request.user_id)
            checklist = _extract_text_from_raw(raw)
        except ConnectionError as e:
            raise HTTPException(status_code=502, detail=f"元器调用失败(兜底): {str(e)}") from e

    if not checklist:
        return {
            "checklist": "",
            "detail": "元器返回成功但未提取到文本，请检查元器工作流输出节点是否写入 message.content/output 字段。"
        }
    return {"checklist": checklist}


@app.post("/evidence/checklist")
async def generate_evidence_checklist(request: ChecklistRequest):
    if not yuanqi_service:
        raise HTTPException(status_code=503, detail="元器服务未配置，请检查 YUANQI_API_KEY 和 YUANQI_ASSISTANT_ID")
    prompt = f"""你是一名法律取证助手。请输出“证据材料清单”。

输出要求：
1. 用 Markdown 表格，列为：证据类别 | 具体材料 | 获取方式 | 注意事项 | 证明目的
2. 最后补充“证据保全建议”小节（3-5条）
3. 面向中国基层纠纷场景，强调可执行性

纠纷描述：
{request.incident}

附加信息：
{request.context or "无"}
"""
    try:
        result = await yuanqi_service.chat(prompt, request.user_id)
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=f"元器调用失败: {str(e)}") from e
    evidence_checklist = (result.get("response", "") or "").strip()
    if not evidence_checklist:
        try:
            raw = await yuanqi_service.chat_raw(prompt, request.user_id)
            evidence_checklist = _extract_text_from_raw(raw)
        except ConnectionError as e:
            raise HTTPException(status_code=502, detail=f"元器调用失败(兜底): {str(e)}") from e

    if not evidence_checklist:
        return {
            "evidence_checklist": "",
            "detail": "元器返回成功但未提取到文本，请检查元器工作流输出节点字段。"
        }
    return {"evidence_checklist": evidence_checklist}


@app.get("/consultations/recent")
async def list_recent_consultations(
    limit: int = Query(default=8, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    rows = await ConsultationRepository.list_recent(db, limit=limit)
    return {"items": [row.to_dict() for row in rows]}


@app.get("/consultations/{consultation_id}/lawsuit")
async def generate_lawsuit(
    consultation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """调用元器生成起诉状结构化字段"""
    if not yuanqi_service:
        raise HTTPException(status_code=503, detail="元器服务未配置，请检查环境变量")

    consultation = await ConsultationRepository.get(db, consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="咨询记录未找到")

    try:
        yuanqi_result = await yuanqi_service.generate_lawsuit_fields(
            case_facts=consultation.query,
            legal_advice=consultation.response or '无',
            evidence_list='',
            user_id=f"lawsuit_{consultation_id}",
        )
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=f"诉状生成失败: {str(e)}") from e

    return yuanqi_result


@app.post("/consultations/{consultation_id}/lawsuit/fields")
async def generate_lawsuit_fields(
    consultation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """表单填充模式 - 调用元器生成结构化字段"""
    if not yuanqi_service:
        raise HTTPException(status_code=503, detail="元器服务未配置，请检查环境变量")

    consultation = await ConsultationRepository.get(db, consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="咨询记录未找到")

    try:
        yuanqi_result = await yuanqi_service.generate_lawsuit_fields(
            case_facts=consultation.query,
            legal_advice=consultation.response or '无',
            evidence_list='',
            user_id=f"lawsuit_fields_{consultation_id}",
        )
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=f"字段生成失败: {str(e)}") from e

    return yuanqi_result


@app.post("/calculator/overtime")
async def calc_overtime(request: OvertimeCalcRequest):
    result = calculator_service.calc_overtime_pay(
        monthly_salary=request.monthly_salary,
        overtime_hours_weekday=request.overtime_hours_weekday,
        overtime_hours_restday=request.overtime_hours_restday,
        overtime_hours_holiday=request.overtime_hours_holiday,
    )
    return result.__dict__


@app.post("/calculator/compensation")
async def calc_compensation(request: CompensationCalcRequest):
    result = calculator_service.calc_compensation(
        monthly_salary=request.monthly_salary,
        worked_years=request.worked_years,
    )
    return result.__dict__


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)