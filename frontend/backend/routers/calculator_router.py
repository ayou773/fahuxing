"""
计算器路由
处理计算器相关的API请求
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from ..services.calculator_service import calculator_service

router = APIRouter()


@router.post("/calculate/overtime")
async def calculate_overtime(data: Dict[str, Any]):
    """
    计算加班费

    Args:
        data: 包含计算参数的字典
            base_salary: 基本工资
            overtime_hours: 加班小时数
            month_days: 每月工作天数（可选，默认21.75）

    Returns:
        计算结果
    """
    try:
        base_salary = data.get('base_salary')
        overtime_hours = data.get('overtime_hours')
        month_days = data.get('month_days', 21.75)

        if base_salary is None or overtime_hours is None:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        result = calculator_service.calculate_overtime_pay(
            base_salary=base_salary,
            overtime_hours=overtime_hours,
            month_days=month_days
        )

        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('message', 'Calculation failed'))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate/severance")
async def calculate_severance(data: Dict[str, Any]):
    """
    计算经济补偿金

    Args:
        data: 包含计算参数的字典
            monthly_salary: 月工资
            years_of_service: 工作年限

    Returns:
        计算结果
    """
    try:
        monthly_salary = data.get('monthly_salary')
        years_of_service = data.get('years_of_service')

        if monthly_salary is None or years_of_service is None:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        result = calculator_service.calculate_severance_pay(
            monthly_salary=monthly_salary,
            years_of_service=years_of_service
        )

        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('message', 'Calculation failed'))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate/social-insurance")
async def calculate_social_insurance(data: Dict[str, Any]):
    """
    计算五险一金

    Args:
        data: 包含计算参数的字典
            monthly_salary: 月工资（缴费基数）

    Returns:
        计算结果
    """
    try:
        monthly_salary = data.get('monthly_salary')

        if monthly_salary is None:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        result = calculator_service.calculate_social_insurance(
            monthly_salary=monthly_salary
        )

        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('message', 'Calculation failed'))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate/individual-tax")
async def calculate_individual_tax(data: Dict[str, Any]):
    """
    计算个人所得税

    Args:
        data: 包含计算参数的字典
            monthly_income: 月收入
            special_deductions: 专项扣除（可选，默认5000）

    Returns:
        计算结果
    """
    try:
        monthly_income = data.get('monthly_income')
        special_deductions = data.get('special_deductions', 5000)

        if monthly_income is None:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        result = calculator_service.calculate_individual_income_tax(
            monthly_income=monthly_income,
            special_deductions=special_deductions
        )

        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('message', 'Calculation failed'))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate/all")
async def calculate_all(data: Dict[str, Any]):
    """
    综合计算所有项目

    Args:
        data: 包含计算参数的字典
            base_salary: 基本工资
            overtime_hours: 加班小时数（可选）
            years_of_service: 工作年限（可选）
            monthly_income: 月收入（可选）

    Returns:
        所有计算结果
    """
    try:
        base_salary = data.get('base_salary')
        overtime_hours = data.get('overtime_hours', 0)
        years_of_service = data.get('years_of_service', 0)
        monthly_income = data.get('monthly_income', 0)

        if base_salary is None:
            raise HTTPException(status_code=400, detail="Missing base_salary parameter")

        result = calculator_service.calculate_all(
            base_salary=base_salary,
            overtime_hours=overtime_hours,
            years_of_service=years_of_service,
            monthly_income=monthly_income
        )

        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('message', 'Calculation failed'))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))