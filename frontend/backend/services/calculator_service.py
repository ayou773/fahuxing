"""
劳资计算器服务
实现加班费、经济补偿金、个税、五险一金等计算功能
"""

import math
from typing import Dict, Any


class CalculatorService:
    """劳资计算器服务类"""

    def __init__(self):
        # 基础配置参数
        self.overtime_rate = 1.5  # 加班费倍率（1.5倍）
        self.severance_pay_rate = 0.5  # 经济补偿金倍率（N+0.5）
        self.social_insurance_rates = {
            'pension': 0.08,    # 养老保险 8%
            'medical': 0.02,    # 医疗保险 2%
            'unemployment': 0.005,  # 失业保险 0.5%
            'housing': 0.12,    # 住房公积金 12%
            'injury': 0.0005,   # 工伤保险 0.05%
            'maternity': 0.0008  # 生育保险 0.08%
        }
        self.tax_brackets = [
            (0, 36000, 0.03, 0),
            (36000, 144000, 0.1, 2520),
            (144000, 300000, 0.2, 16920),
            (300000, 420000, 0.25, 31920),
            (420000, 660000, 0.3, 52920),
            (660000, 960000, 0.35, 85920),
            (960000, float('inf'), 0.45, 181920)
        ]

    def calculate_overtime_pay(self, base_salary: float, overtime_hours: float, month_days: int = 21.75) -> Dict[str, Any]:
        """
        计算加班费

        Args:
            base_salary: 基本工资（月）
            overtime_hours: 加班小时数
            month_days: 每月工作天数（默认21.75天）

        Returns:
            包含计算结果的字典
        """
        try:
            # 计算日工资
            daily_salary = base_salary / month_days
            # 计算小时工资
            hourly_salary = daily_salary / 8

            # 计算加班费
            overtime_pay = hourly_salary * self.overtime_rate * overtime_hours

            return {
                'success': True,
                'base_salary': base_salary,
                'overtime_hours': overtime_hours,
                'hourly_salary': round(hourly_salary, 2),
                'overtime_pay': round(overtime_pay, 2),
                'overtime_rate': self.overtime_rate
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '加班费计算失败'
            }

    def calculate_severance_pay(self, monthly_salary: float, years_of_service: float) -> Dict[str, Any]:
        """
        计算经济补偿金（N+0.5）

        Args:
            monthly_salary: 月工资
            years_of_service: 工作年限

        Returns:
            包含计算结果的字典
        """
        try:
            # 计算经济补偿金
            severance_pay = monthly_salary * (years_of_service + self.severance_pay_rate)

            return {
                'success': True,
                'monthly_salary': monthly_salary,
                'years_of_service': years_of_service,
                'severance_pay': round(severance_pay, 2),
                'severance_pay_rate': self.severance_pay_rate
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '经济补偿金计算失败'
            }

    def calculate_social_insurance(self, monthly_salary: float) -> Dict[str, Any]:
        """
        计算五险一金

        Args:
            monthly_salary: 月工资（缴费基数）

        Returns:
            包含计算结果的字典
        """
        try:
            results = {}
            total_insurance = 0

            for name, rate in self.social_insurance_rates.items():
                amount = monthly_salary * rate
                results[name] = round(amount, 2)
                total_insurance += amount

            results['total'] = round(total_insurance, 2)
            results['base_salary'] = monthly_salary

            return {
                'success': True,
                'social_insurance': results,
                'total_insurance': results['total']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '五险一金计算失败'
            }

    def calculate_individual_income_tax(self, monthly_income: float, special_deductions: float = 5000) -> Dict[str, Any]:
        """
        计算个人所得税

        Args:
            monthly_income: 月收入
            special_deductions: 专项扣除（默认5000元）

        Returns:
            包含计算结果的字典
        """
        try:
            # 计算应纳税所得额
            taxable_income = monthly_income - special_deductions

            if taxable_income <= 0:
                return {
                    'success': True,
                    'monthly_income': monthly_income,
                    'taxable_income': 0,
                    'tax_amount': 0,
                    'after_tax_income': monthly_income
                }

            # 查找适用的税率
            tax_amount = 0
            for bracket in self.tax_brackets:
                lower, upper, rate, deduction = bracket
                if lower < taxable_income <= upper:
                    tax_amount = taxable_income * rate - deduction
                    break

            after_tax_income = monthly_income - tax_amount

            return {
                'success': True,
                'monthly_income': monthly_income,
                'special_deductions': special_deductions,
                'taxable_income': round(taxable_income, 2),
                'tax_amount': round(tax_amount, 2),
                'after_tax_income': round(after_tax_income, 2)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '个税计算失败'
            }

    def calculate_all(self, base_salary: float, overtime_hours: float = 0, years_of_service: float = 0,
                    monthly_income: float = 0) -> Dict[str, Any]:
        """
        综合计算所有项目

        Args:
            base_salary: 基本工资
            overtime_hours: 加班小时数
            years_of_service: 工作年限
            monthly_income: 月收入（用于个税计算）

        Returns:
            包含所有计算结果的字典
        """
        results = {}

        # 计算加班费
        if overtime_hours > 0:
            results['overtime'] = self.calculate_overtime_pay(base_salary, overtime_hours)

        # 计算经济补偿金
        if years_of_service > 0:
            results['severance'] = self.calculate_severance_pay(base_salary, years_of_service)

        # 计算五险一金
        results['social_insurance'] = self.calculate_social_insurance(base_salary)

        # 计算个税
        if monthly_income > 0:
            results['individual_tax'] = self.calculate_individual_income_tax(monthly_income)

        return {
            'success': all(result.get('success', False) for result in results.values()),
            'calculations': results
        }


# 服务实例
calculator_service = CalculatorService()