'use client';

import { useState } from 'react';
import MarkdownContent from '@/components/MarkdownContent';

export default function CalculatorPanel() {
  const [calcType, setCalcType] = useState<'overtime' | 'compensation'>('overtime');
  const [monthlySalary, setMonthlySalary] = useState('');
  const [weekdayHours, setWeekdayHours] = useState('0');
  const [restdayHours, setRestdayHours] = useState('0');
  const [holidayHours, setHolidayHours] = useState('0');
  const [workedYears, setWorkedYears] = useState('');
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  const calculate = async () => {
    if (!monthlySalary || parseFloat(monthlySalary) <= 0) return;
    setLoading(true);
    setResult(null);
    try {
      const url = calcType === 'overtime'
        ? '/api/calculator/overtime'
        : '/api/calculator/compensation';
      const body = calcType === 'overtime'
        ? {
            monthly_salary: parseFloat(monthlySalary),
            overtime_hours_weekday: parseFloat(weekdayHours) || 0,
            overtime_hours_restday: parseFloat(restdayHours) || 0,
            overtime_hours_holiday: parseFloat(holidayHours) || 0,
          }
        : {
            monthly_salary: parseFloat(monthlySalary),
            worked_years: parseFloat(workedYears) || 0,
          };
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error('计算失败');
      const data = await res.json();
      setResult(data);
    } catch {
      setResult({ error: '计算服务暂时不可用' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex gap-3">
        <button
          onClick={() => { setCalcType('overtime'); setResult(null); }}
          className={`flex-1 rounded-xl py-3 font-semibold transition-all ${
            calcType === 'overtime'
              ? 'bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8a] text-white shadow-md'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          加班费计算
        </button>
        <button
          onClick={() => { setCalcType('compensation'); setResult(null); }}
          className={`flex-1 rounded-xl py-3 font-semibold transition-all ${
            calcType === 'compensation'
              ? 'bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8a] text-white shadow-md'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          经济补偿金计算
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">月工资（元）</label>
          <input
            type="number"
            value={monthlySalary}
            onChange={(e) => setMonthlySalary(e.target.value)}
            placeholder="请输入月薪"
            className="w-full rounded-xl border border-gray-200 p-3 focus:border-[#d4a84b] focus:outline-none focus:ring-2 focus:ring-[#d4a84b]/20"
          />
        </div>

        {calcType === 'overtime' && (
          <>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">工作日加班（小时）</label>
              <input
                type="number"
                value={weekdayHours}
                onChange={(e) => setWeekdayHours(e.target.value)}
                placeholder="1.5倍工资"
                className="w-full rounded-xl border border-gray-200 p-3 focus:border-[#d4a84b] focus:outline-none focus:ring-2 focus:ring-[#d4a84b]/20"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">休息日加班（小时）</label>
              <input
                type="number"
                value={restdayHours}
                onChange={(e) => setRestdayHours(e.target.value)}
                placeholder="2倍工资"
                className="w-full rounded-xl border border-gray-200 p-3 focus:border-[#d4a84b] focus:outline-none focus:ring-2 focus:ring-[#d4a84b]/20"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">法定节假日加班（小时）</label>
              <input
                type="number"
                value={holidayHours}
                onChange={(e) => setHolidayHours(e.target.value)}
                placeholder="3倍工资"
                className="w-full rounded-xl border border-gray-200 p-3 focus:border-[#d4a84b] focus:outline-none focus:ring-2 focus:ring-[#d4a84b]/20"
              />
            </div>
          </>
        )}

        {calcType === 'compensation' && (
          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">工作年限</label>
            <input
              type="number"
              step="0.5"
              value={workedYears}
              onChange={(e) => setWorkedYears(e.target.value)}
              placeholder="例如：2.5"
              className="w-full rounded-xl border border-gray-200 p-3 focus:border-[#d4a84b] focus:outline-none focus:ring-2 focus:ring-[#d4a84b]/20"
            />
          </div>
        )}
      </div>

      <button
        onClick={calculate}
        disabled={loading || !monthlySalary || parseFloat(monthlySalary) <= 0}
        className="w-full rounded-xl bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8a] py-3.5 font-semibold text-white transition-all hover:shadow-md disabled:opacity-50"
      >
        {loading ? '计算中...' : '立即计算'}
      </button>

      {result && (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
          <h3 className="mb-3 font-semibold text-[#1e3a5f]">计算结果</h3>
          {('error' in result) ? (
            <p className="text-red-500">{String(result.error)}</p>
          ) : calcType === 'overtime' ? (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between rounded-lg bg-white p-3">
                <span className="text-slate-600">基础时薪</span>
                <span className="font-semibold text-[#1e3a5f]">¥{String(result.base_hourly_wage)}</span>
              </div>
              <div className="flex justify-between rounded-lg bg-white p-3">
                <span className="text-slate-600">工作日加班费</span>
                <span className="font-semibold text-[#1e3a5f]">¥{String(result.weekday_pay)}</span>
              </div>
              <div className="flex justify-between rounded-lg bg-white p-3">
                <span className="text-slate-600">休息日加班费</span>
                <span className="font-semibold text-[#1e3a5f]">¥{String(result.restday_pay)}</span>
              </div>
              <div className="flex justify-between rounded-lg bg-white p-3">
                <span className="text-slate-600">法定节假日加班费</span>
                <span className="font-semibold text-[#1e3a5f]">¥{String(result.holiday_pay)}</span>
              </div>
              <div className="flex justify-between rounded-lg bg-[#d4a84b]/10 p-3">
                <span className="font-semibold text-[#1e3a5f]">加班费合计</span>
                <span className="font-bold text-[#d4a84b] text-lg">¥{String(result.total_overtime_pay)}</span>
              </div>
            </div>
          ) : (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between rounded-lg bg-white p-3">
                <span className="text-slate-600">月工资</span>
                <span className="font-semibold text-[#1e3a5f]">¥{String(result.monthly_salary)}</span>
              </div>
              <div className="flex justify-between rounded-lg bg-white p-3">
                <span className="text-slate-600">工作年限</span>
                <span className="font-semibold text-[#1e3a5f]">{String(result.worked_years)} 年</span>
              </div>
              <div className="flex justify-between rounded-lg bg-white p-3">
                <span className="text-slate-600">补偿月数</span>
                <span className="font-semibold text-[#1e3a5f]">{String(result.compensation_months)} 个月</span>
              </div>
              <div className="flex justify-between rounded-lg bg-[#d4a84b]/10 p-3">
                <span className="font-semibold text-[#1e3a5f]">经济补偿金</span>
                <span className="font-bold text-[#d4a84b] text-lg">¥{String(result.compensation_amount)}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
