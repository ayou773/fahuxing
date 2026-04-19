from dataclasses import dataclass


@dataclass
class OvertimeResult:
    overtime_hours: float
    base_hourly_wage: float
    weekday_pay: float
    restday_pay: float
    holiday_pay: float
    total_overtime_pay: float


@dataclass
class CompensationResult:
    monthly_salary: float
    worked_years: float
    compensation_months: float
    compensation_amount: float


class CalculatorService:
    """维权计算工具：加班费与经济补偿金"""

    @staticmethod
    def calc_overtime_pay(
        monthly_salary: float,
        overtime_hours_weekday: float = 0.0,
        overtime_hours_restday: float = 0.0,
        overtime_hours_holiday: float = 0.0,
        legal_working_days: float = 21.75,
        legal_daily_hours: float = 8.0,
    ) -> OvertimeResult:
        base_hourly_wage = monthly_salary / legal_working_days / legal_daily_hours
        weekday_pay = overtime_hours_weekday * base_hourly_wage * 1.5
        restday_pay = overtime_hours_restday * base_hourly_wage * 2.0
        holiday_pay = overtime_hours_holiday * base_hourly_wage * 3.0
        total = weekday_pay + restday_pay + holiday_pay
        return OvertimeResult(
            overtime_hours=overtime_hours_weekday + overtime_hours_restday + overtime_hours_holiday,
            base_hourly_wage=round(base_hourly_wage, 2),
            weekday_pay=round(weekday_pay, 2),
            restday_pay=round(restday_pay, 2),
            holiday_pay=round(holiday_pay, 2),
            total_overtime_pay=round(total, 2),
        )

    @staticmethod
    def calc_compensation(monthly_salary: float, worked_years: float) -> CompensationResult:
        # 常见规则简化版：工作每满1年支付1个月工资；6个月以上不满1年按1年；不满6个月按0.5个月
        years_int = int(worked_years)
        remainder = worked_years - years_int
        extra = 1.0 if remainder >= 0.5 else (0.5 if remainder > 0 else 0.0)
        months = years_int + extra
        amount = monthly_salary * months
        return CompensationResult(
            monthly_salary=round(monthly_salary, 2),
            worked_years=round(worked_years, 2),
            compensation_months=round(months, 2),
            compensation_amount=round(amount, 2),
        )
