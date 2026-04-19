from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from services.document_service import DocumentService

router = APIRouter(prefix="/lawsuit", tags=["lawsuit"])


class LawsuitFormRequest(BaseModel):
    """基于表单生成起诉状的请求"""
    plaintiff_name: str = ""
    plaintiff_gender: str = ""
    plaintiff_birth: str = ""
    plaintiff_address: str = ""
    plaintiff_phone: str = ""
    defendant_name: str = ""
    defendant_address: str = ""
    defendant_phone: str = ""
    claims: str = ""
    court_name: str = ""
    facts_and_reasons: str = ""
    evidence_list: str = ""
    legal_basis: str = ""


@router.post("/generate-from-form")
async def generate_from_form(data: LawsuitFormRequest):
    """从表单直接生成起诉状（不依赖 AI）"""
    ds = DocumentService()
    now = datetime.now()

    claims_list = [c.strip() for c in data.claims.split("\n") if c.strip()] if data.claims else []
    evidence_list = [e.strip() for e in data.evidence_list.split("\n") if e.strip()] if data.evidence_list else []

    lawsuit_data = {
        "plaintiff_name": data.plaintiff_name or "原告姓名",
        "plaintiff_gender": data.plaintiff_gender,
        "plaintiff_birth": data.plaintiff_birth,
        "plaintiff_address": data.plaintiff_address,
        "plaintiff_phone": data.plaintiff_phone,
        "defendant_name": data.defendant_name or "被告姓名/单位名称",
        "defendant_address": data.defendant_address,
        "defendant_phone": data.defendant_phone,
        "claims": claims_list,
        "court_name": data.court_name or "XX市XX区人民法院",
        "facts_and_reasons": data.facts_and_reasons,
        "evidence_list": evidence_list,
        "legal_basis": data.legal_basis,
        "class_cases": "",
        "date_year": str(now.year),
        "date_month": str(now.month),
        "date_day": str(now.day),
    }

    try:
        document_text = ds.generate_lawsuit(lawsuit_data)
        return {"document": document_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文书生成失败: {str(e)}")


@router.post("/template-fields")
async def get_template_fields():
    """返回起诉状模板所需字段说明"""
    ds = DocumentService()
    return ds.generate_template_fields()
