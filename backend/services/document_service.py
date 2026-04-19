import jinja2
import os
from typing import Dict, Any, List
from datetime import datetime


class DocumentService:
    """文书生成服务 - 基于标准民事起诉状模板"""

    TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

    def __init__(self):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=False,
        )

    def generate_lawsuit(self, data: Dict[str, Any]) -> str:
        """根据结构化数据生成标准民事起诉状"""
        now = datetime.now()
        template = self.env.get_template("lawsuit_standard.j2")
        return template.render(
            plaintiff_name=data.get("plaintiff_name", "原告姓名"),
            plaintiff_gender=data.get("plaintiff_gender", ""),
            plaintiff_birth=data.get("plaintiff_birth", ""),
            plaintiff_address=data.get("plaintiff_address", ""),
            plaintiff_phone=data.get("plaintiff_phone", ""),
            defendant_name=data.get("defendant_name", "被告姓名/单位名称"),
            defendant_address=data.get("defendant_address", ""),
            defendant_phone=data.get("defendant_phone", ""),
            claims=data.get("claims", []),
            court_name=data.get("court_name", "XX市XX区人民法院"),
            facts_and_reasons=data.get("facts_and_reasons", ""),
            evidence_list=data.get("evidence_list", []),
            legal_basis=data.get("legal_basis", ""),
            class_cases=data.get("class_cases", ""),
            date_year=data.get("date_year", str(now.year)),
            date_month=data.get("date_month", str(now.month)),
            date_day=data.get("date_day", str(now.day)),
        )

    def generate_template_fields(self) -> Dict[str, Any]:
        """返回模板所需字段说明，用于前端表单生成"""
        return {
            "plaintiff_name": {"label": "原告姓名", "type": "text", "required": True, "placeholder": "姓名"},
            "plaintiff_gender": {"label": "性别", "type": "text", "required": False, "placeholder": "男/女"},
            "plaintiff_birth": {"label": "出生年月", "type": "text", "required": False, "placeholder": "1990年1月"},
            "plaintiff_address": {"label": "住址", "type": "text", "required": False, "placeholder": "详细地址"},
            "plaintiff_phone": {"label": "联系方式", "type": "text", "required": False, "placeholder": "手机号"},
            "defendant_name": {"label": "被告姓名/单位名称", "type": "text", "required": True, "placeholder": "姓名或公司全称"},
            "defendant_address": {"label": "被告地址", "type": "text", "required": False, "placeholder": "详细地址"},
            "defendant_phone": {"label": "被告联系方式", "type": "text", "required": False, "placeholder": "手机号"},
            "claims": {"label": "诉讼请求", "type": "textarea", "required": True, "placeholder": "每行一项，例如：\n1. 判令被告支付拖欠工资XX元\n2. 判令被告支付经济补偿金XX元"},
            "court_name": {"label": "管辖法院", "type": "text", "required": False, "placeholder": "XX市XX区人民法院"},
            "facts_and_reasons": {"label": "事实与理由", "type": "textarea", "required": True, "placeholder": "详细描述纠纷经过"},
            "evidence_list": {"label": "证据清单", "type": "textarea", "required": False, "placeholder": "每行一项证据"},
            "legal_basis": {"label": "法律依据", "type": "textarea", "required": False, "placeholder": "相关法条（选填）"},
        }

    async def generate_contract_review(self, consultation_data: Dict[str, Any]) -> str:
        """生成合同审查意见书（扩展预留）"""
        template = self.env.get_template("contract_review.j2")
        return template.render(consultation_data)
