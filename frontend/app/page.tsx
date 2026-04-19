'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import MarkdownContent from '@/components/MarkdownContent';
import CalculatorPanel from '@/components/calculator/CalculatorPanel';
import { useToast } from '@/components/Toast';

type TabType = 'consult' | 'rights' | 'evidence' | 'document' | 'calculator';

interface TabConfig {
  id: TabType;
  icon: string;
  label: string;
  description: string;
  tip: string;
}

const tabs: TabConfig[] = [
  { id: 'consult', icon: '⚖️', label: '法律咨询', description: '描述纠纷事实，AI 提供专业法律分析', tip: '尽量详细描述时间、地点、涉及人员和金额，这样 AI 能给出更准确的建议' },
  { id: 'rights', icon: '🧭', label: '维权清单', description: '生成分阶段行动方案，按时间节点规划', tip: '基于您描述的纠纷自动规划 24小时 / 7天 / 30天 的维权行动' },
  { id: 'evidence', icon: '🗂️', label: '证据清单', description: '自动生成证据材料清单与保全建议', tip: '列出您需要收集的证据类型、获取方式和注意事项' },
  { id: 'document', icon: '📝', label: '文书生成', description: '基于咨询记录一键生成起诉状', tip: '需要咨询记录 ID，请先在"法律咨询"中完成咨询获取 ID' },
  { id: 'calculator', icon: '🧮', label: '计算器', description: '加班费与经济补偿金快速估算', tip: '输入月薪和工作年限即可快速计算加班费或经济补偿金' },
];

export default function Home() {
  const { addToast } = useToast();
  const currentYear = new Date().getFullYear();
  const [activeTab, setActiveTab] = useState<TabType>('consult');
  const [query, setQuery] = useState('');
  const [context, setContext] = useState('');
  const [userId, setUserId] = useState('guest_user');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [consultationId, setConsultationId] = useState<string | null>(null);
  const [storedResult, setStoredResult] = useState<string | null>(null);
  const [storedConsultId, setStoredConsultId] = useState<string | null>(null);
  const [lawsuitInputId, setLawsuitInputId] = useState('');
  const [lawsuitLoading, setLawsuitLoading] = useState(false);
  const [formData, setFormData] = useState({
    plaintiff_name: '',
    plaintiff_gender: '',
    plaintiff_birth: '',
    plaintiff_address: '',
    plaintiff_phone: '',
    defendant_name: '',
    defendant_address: '',
    defendant_phone: '',
    claims: '',
    court_name: '',
    facts_and_reasons: '',
    evidence_list: '',
    legal_basis: '',
  });
  const [copied, setCopied] = useState(false);
  const [history, setHistory] = useState<Array<{ id: string; query: string; created_at: string }>>([]);
  const [historyLoaded, setHistoryLoaded] = useState(false);

  useEffect(() => {
    const savedResult = localStorage.getItem('fahuxing_latest_result');
    const savedId = localStorage.getItem('fahuxing_latest_consultation_id');
    if (savedResult) {
      setResult(savedResult);
      setStoredResult(savedResult);
    }
    if (savedId) {
      setConsultationId(savedId);
      setStoredConsultId(savedId);
      setLawsuitInputId(savedId);
    }
    fetch('/api/consultations/recent?limit=8')
      .then((res) => res.json())
      .then((data) => {
        if (data.items && data.items.length > 0) {
          setHistory(data.items);
        }
        setHistoryLoaded(true);
      })
      .catch(() => setHistoryLoaded(true));
  }, []);

  useEffect(() => {
    localStorage.setItem('fahuxing_user_id', userId);
  }, [userId]);

  useEffect(() => {
    if (storedResult) {
      localStorage.setItem('fahuxing_latest_result', storedResult);
    }
  }, [storedResult]);

  useEffect(() => {
    if (storedConsultId) {
      localStorage.setItem('fahuxing_latest_consultation_id', storedConsultId);
    }
  }, [storedConsultId]);

  const runRequest = async (url: string, body: Record<string, string>, resultKey: string) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const raw = await res.text();
      let data: Record<string, unknown> = {};
      try {
        data = raw ? JSON.parse(raw) : {};
      } catch {
        data = { detail: raw || '服务返回了非 JSON 内容' };
      }
      if (!res.ok) throw new Error((data.detail as string) || '请求失败');
      const resultText = (data[resultKey] as string) || '未返回结果';
      setResult(resultText);
      setStoredResult(resultText);
      if (data.consultation_id) {
        setConsultationId(data.consultation_id as string);
        setStoredConsultId(data.consultation_id as string);
        localStorage.setItem('fahuxing_latest_consultation_id', data.consultation_id as string);
        addToast('咨询记录已保存', 'success');
        fetch('/api/consultations/recent?limit=8')
          .then((r) => r.json())
          .then((d) => { if (d.items) setHistory(d.items); })
          .catch(() => {});
      }
    } catch (error) {
      const msg = error instanceof Error ? error.message : '服务暂时不可用';
      setResult(msg);
      addToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleConsult = async () => {
    if (!query.trim()) { addToast('请输入纠纷问题', 'warning'); return; }
    await runRequest('/api/consultation', { query, context, user_id: userId }, 'response');
  };

  const handleRightsChecklist = async () => {
    if (!query.trim()) { addToast('请输入纠纷问题', 'warning'); return; }
    await runRequest('/api/rights/checklist', { incident: query, context, user_id: userId }, 'checklist');
  };

  const handleEvidenceChecklist = async () => {
    if (!query.trim()) { addToast('请输入纠纷问题', 'warning'); return; }
    await runRequest('/api/evidence/checklist', { incident: query, context, user_id: userId }, 'evidence_checklist');
  };

  const handleGenerateLawsuitFields = async () => {
    const targetId = (lawsuitInputId || storedConsultId || '').trim();
    if (!targetId) { addToast('请先输入咨询记录ID', 'warning'); return; }
    setLawsuitLoading(true);
    try {
      const res = await fetch(`/api/consultations/${targetId}/lawsuit`);
      const raw = await res.text();
      let data: Record<string, unknown> = {};
      try { data = raw ? JSON.parse(raw) : {}; } catch { data = { detail: raw || '服务返回了非 JSON 内容' }; }
      if (!res.ok) throw new Error((data.detail as string) || '字段生成失败');
      
      if (data.success && data.fields) {
        const fields = data.fields as Record<string, string>;
        setFormData({
          ...formData,
          claims: fields.claims || '',
          facts_and_reasons: fields.facts_and_reasons || '',
          legal_basis: fields.legal_basis || '',
          evidence_list: fields.evidence_list || '',
        });
        addToast('AI 已智能填充表单，请检查并补充信息', 'success');
      } else {
        addToast('字段生成失败，请重试', 'error');
      }
    } catch (error) { addToast(error instanceof Error ? error.message : '字段生成失败', 'error'); }
    finally { setLawsuitLoading(false); }
  };

  const handleGenerateLawsuitFromForm = async () => {
    if (!formData.plaintiff_name.trim() || !formData.defendant_name.trim()) {
      addToast('请填写原告和被告姓名', 'warning');
      return;
    }
    if (!formData.claims.trim()) {
      addToast('请填写诉讼请求', 'warning');
      return;
    }
    if (!formData.facts_and_reasons.trim()) {
      addToast('请填写事实与理由', 'warning');
      return;
    }
    setLawsuitLoading(true);
    try {
      const res = await fetch('/api/lawsuit/generate-from-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const raw = await res.text();
      let data: Record<string, unknown> = {};
      try { data = raw ? JSON.parse(raw) : {}; } catch { data = { detail: raw || '服务返回了非 JSON 内容' }; }
      if (!res.ok) throw new Error((data.detail as string) || '文书生成失败');
      const doc = (data.document as string) || '未返回文书内容';
      setResult(doc);
      setStoredResult(doc);
      addToast('起诉状生成成功', 'success');
    } catch (error) { addToast(error instanceof Error ? error.message : '文书生成失败', 'error'); }
    finally { setLawsuitLoading(false); }
  };

  const handleCopyResult = async () => {
    if (!result) return;
    try { await navigator.clipboard.writeText(result); setCopied(true); addToast('已复制到剪贴板', 'success'); setTimeout(() => setCopied(false), 1500); } catch { setCopied(false); }
  };

  const currentTab = tabs.find((t) => t.id === activeTab);
  const isConsultTab = activeTab === 'consult' || activeTab === 'rights' || activeTab === 'evidence';

  const getPlaceholder = () => {
    if (activeTab === 'consult') return '例如：房东拒不退押金并扣除不合理费用';
    if (activeTab === 'rights') return '例如：公司无故辞退，未支付经济补偿';
    if (activeTab === 'evidence') return '例如：与同事发生劳务纠纷，需要收集证据';
    return '';
  };

  const getButtonText = () => {
    if (activeTab === 'consult') return loading ? 'AI 正在分析...' : '获取法律建议';
    if (activeTab === 'rights') return loading ? '生成中...' : '生成维权清单';
    if (activeTab === 'evidence') return loading ? '生成中...' : '生成证据清单';
    return '';
  };

  const getButtonHandler = () => {
    if (activeTab === 'consult') return handleConsult;
    if (activeTab === 'rights') return handleRightsChecklist;
    if (activeTab === 'evidence') return handleEvidenceChecklist;
    return () => {};
  };

  const steps = [
    { num: '01', title: '法律咨询', desc: '在左侧选择"法律咨询"，输入纠纷事实，点击"获取法律建议"。系统会自动生成咨询记录 ID。', icon: '⚖️' },
    { num: '02', title: '维权 / 证据清单', desc: '切换到对应功能，系统基于您的纠纷描述，生成可执行的行动方案或证据采集列表。', icon: '📋' },
    { num: '03', title: '文书生成', desc: '进入"文书生成"，填入咨询记录 ID，一键生成起诉状草稿，可直接使用或进一步修改。', icon: '📝' },
    { num: '04', title: '金额估算', desc: '使用"计算器"功能，快速计算加班费或经济补偿金，为维权提供参考依据。', icon: '🧮' },
  ];

  return (
    <div className="min-h-screen bg-[#f5f6fa] flex flex-col">
      <header className="bg-white border-b border-slate-200/80 px-4 md:px-6 py-3 flex items-center justify-between sticky top-0 z-50">
        <Link href="/" className="flex items-center gap-3">
          <Image src="/logo1.png" alt="法护星" width={32} height={32} className="w-8 h-8 rounded-lg object-contain" />
          <span className="text-lg font-bold text-[#1e3a5f]">法护星</span>
        </Link>
        <span className="text-xs text-slate-400">基层纠纷智慧维权</span>
      </header>

      <div className="flex-1 flex flex-col lg:flex-row max-w-[1440px] w-full mx-auto">
        <aside className="lg:w-60 xl:w-72 bg-white border-r border-slate-200/80 flex-shrink-0">
          <div className="p-4">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest mb-3 px-1">功能选择</p>
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => { setActiveTab(tab.id); setResult(null); }}
                  className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl text-left transition-all ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8a] text-white shadow-md shadow-[#1e3a5f]/15'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className="text-xl flex-shrink-0 leading-none">{tab.icon}</span>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold truncate">{tab.label}</p>
                    <p className={`text-[11px] truncate ${activeTab === tab.id ? 'text-white/60' : 'text-slate-400'}`}>{tab.description}</p>
                  </div>
                </button>
              ))}
            </nav>
          </div>

          <div className="mx-4 mb-4 p-4 rounded-xl bg-gradient-to-br from-[#1e3a5f] to-[#0f2240] text-white">
            <p className="text-sm font-bold mb-2 flex items-center gap-2">
              <svg className="w-5 h-5 text-[#d4a84b]" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" /></svg>
              操作提示
            </p>
            <p className="text-sm leading-relaxed text-white/80">{currentTab?.tip}</p>
          </div>
        </aside>

        <main className="flex-1 min-w-0 flex flex-col">
          <div className="flex-1 mx-4 my-4">
            <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden h-full flex flex-col">
              <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-3 flex-shrink-0">
                <span className="text-2xl">{currentTab?.icon}</span>
                <div>
                  <h2 className="text-base font-bold text-[#1e3a5f]">{currentTab?.label}</h2>
                  <p className="text-xs text-slate-500">{currentTab?.description}</p>
                </div>
              </div>

              <div className="p-5 flex-1 overflow-y-auto">
                {isConsultTab && (
                  <div className="space-y-5 max-w-2xl">
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <label className="mb-1.5 block text-xs font-semibold text-slate-500 uppercase tracking-wide">用户 ID</label>
                        <input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="用于会话隔离"
                          className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10 transition-all" />
                      </div>
                      <div>
                        <label className="mb-1.5 block text-xs font-semibold text-slate-500 uppercase tracking-wide">补充背景</label>
                        <input value={context} onChange={(e) => setContext(e.target.value)} placeholder="时间、地点等"
                          className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10 transition-all" />
                      </div>
                    </div>
                    <div>
                      <label className="mb-1.5 block text-xs font-semibold text-slate-500 uppercase tracking-wide">问题描述</label>
                      <textarea value={query} onChange={(e) => setQuery(e.target.value)} placeholder={getPlaceholder()}
                        className="h-28 w-full resize-none rounded-xl border border-slate-200 px-4 py-3 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10 transition-all" />
                    </div>
                    <button onClick={getButtonHandler()} disabled={loading || !query.trim()}
                      className="w-full rounded-xl bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8a] py-3 font-semibold text-white transition-all hover:shadow-lg hover:shadow-[#1e3a5f]/15 disabled:opacity-50 flex items-center justify-center gap-2">
                      {loading ? <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                        : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
                      {getButtonText()}
                    </button>

                    {consultationId && activeTab === 'consult' && (
                      <div className="flex items-center gap-3 text-sm bg-blue-50 text-blue-700 p-3.5 rounded-xl border border-blue-100">
                        <svg className="w-5 h-5 text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                        <span>咨询记录 ID：<span className="font-mono font-semibold text-blue-800">{consultationId}</span></span>
                      </div>
                    )}

                    {result && (
                      <div className="rounded-xl border border-slate-200 bg-slate-50/50">
                        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
                          <h3 className="font-semibold text-sm text-[#1e3a5f]">AI 输出结果</h3>
                          <button onClick={handleCopyResult} className={`text-xs px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1 ${copied ? 'border-green-200 bg-green-50 text-green-600' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'}`}>
                            {copied ? <>✓ 已复制</> : <>📋 复制</>}
                          </button>
                        </div>
                        <div className="p-4">
                          <MarkdownContent content={result} className="max-h-[480px] overflow-y-auto text-sm" />
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'document' && (
                  <div className="space-y-5 max-w-2xl">
                    <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-semibold text-blue-800">AI 智能生成起诉状</p>
                          <p className="text-xs text-blue-600 mt-1 leading-relaxed">基于咨询记录，元器自动分析案情并智能填充表单字段。填充后可编辑修改，然后生成标准格式起诉状。</p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="mb-1.5 block text-xs font-semibold text-slate-500 uppercase tracking-wide">咨询记录 ID</label>
                      <div className="flex gap-3">
                        <input value={lawsuitInputId} onChange={(e) => setLawsuitInputId(e.target.value)} placeholder={storedConsultId ? `例如：${storedConsultId}` : '请输入咨询记录 ID'}
                          className="flex-1 rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10 transition-all" />
                        <button onClick={handleGenerateLawsuitFields} disabled={lawsuitLoading}
                          className="rounded-xl bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8a] px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-60 transition-all hover:shadow-lg hover:shadow-[#1e3a5f]/15 flex items-center gap-2 flex-shrink-0">
                          {lawsuitLoading ? <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg> : '🤖'}
                          AI 智能填充
                        </button>
                      </div>
                    </div>
                    {storedConsultId && <button onClick={() => { setLawsuitInputId(storedConsultId); addToast('已自动填入咨询ID', 'success'); }} className="text-sm text-[#1e3a5f] hover:text-[#d4a84b] transition-colors">使用最近咨询 ID：{storedConsultId}</button>}
                    
                    <div className="bg-slate-50 rounded-xl p-4 space-y-4 border border-slate-200">
                          <p className="text-sm font-bold text-[#1e3a5f] mb-3">原告信息</p>
                          <div className="grid gap-3 sm:grid-cols-2">
                            <div>
                              <label className="mb-1 block text-xs font-semibold text-slate-600">姓名 <span className="text-red-500">*</span></label>
                              <input value={formData.plaintiff_name} onChange={(e) => setFormData({...formData, plaintiff_name: e.target.value})} placeholder="原告姓名"
                                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                            </div>
                            <div>
                              <label className="mb-1 block text-xs font-semibold text-slate-600">性别</label>
                              <input value={formData.plaintiff_gender} onChange={(e) => setFormData({...formData, plaintiff_gender: e.target.value})} placeholder="男/女"
                                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                            </div>
                            <div>
                              <label className="mb-1 block text-xs font-semibold text-slate-600">出生年月</label>
                              <input value={formData.plaintiff_birth} onChange={(e) => setFormData({...formData, plaintiff_birth: e.target.value})} placeholder="1990年1月"
                                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                            </div>
                            <div>
                              <label className="mb-1 block text-xs font-semibold text-slate-600">联系方式</label>
                              <input value={formData.plaintiff_phone} onChange={(e) => setFormData({...formData, plaintiff_phone: e.target.value})} placeholder="手机号"
                                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                            </div>
                            <div className="sm:col-span-2">
                              <label className="mb-1 block text-xs font-semibold text-slate-600">住址</label>
                              <input value={formData.plaintiff_address} onChange={(e) => setFormData({...formData, plaintiff_address: e.target.value})} placeholder="详细地址"
                                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                            </div>
                          </div>
                        </div>

                        <div className="bg-slate-50 rounded-xl p-4 space-y-4 border border-slate-200">
                          <p className="text-sm font-bold text-[#1e3a5f] mb-3">被告信息</p>
                          <div className="grid gap-3 sm:grid-cols-2">
                            <div>
                              <label className="mb-1 block text-xs font-semibold text-slate-600">姓名/单位 <span className="text-red-500">*</span></label>
                              <input value={formData.defendant_name} onChange={(e) => setFormData({...formData, defendant_name: e.target.value})} placeholder="被告姓名或公司全称"
                                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                            </div>
                            <div>
                              <label className="mb-1 block text-xs font-semibold text-slate-600">联系方式</label>
                              <input value={formData.defendant_phone} onChange={(e) => setFormData({...formData, defendant_phone: e.target.value})} placeholder="手机号"
                                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                            </div>
                            <div className="sm:col-span-2">
                              <label className="mb-1 block text-xs font-semibold text-slate-600">地址</label>
                              <input value={formData.defendant_address} onChange={(e) => setFormData({...formData, defendant_address: e.target.value})} placeholder="详细地址"
                                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                            </div>
                          </div>
                        </div>

                        <div className="bg-slate-50 rounded-xl p-4 space-y-4 border border-slate-200">
                          <p className="text-sm font-bold text-[#1e3a5f] mb-3">诉讼请求 <span className="text-red-500">*</span></p>
                          <textarea value={formData.claims} onChange={(e) => setFormData({...formData, claims: e.target.value})} placeholder={"每行一项，例如：\n1. 判令被告支付拖欠工资XX元\n2. 判令被告支付经济补偿金XX元"}
                            className="w-full h-24 resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                        </div>

                        <div className="bg-slate-50 rounded-xl p-4 space-y-4 border border-slate-200">
                          <p className="text-sm font-bold text-[#1e3a5f] mb-3">事实与理由 <span className="text-red-500">*</span></p>
                          <textarea value={formData.facts_and_reasons} onChange={(e) => setFormData({...formData, facts_and_reasons: e.target.value})} placeholder="详细描述纠纷经过及法律依据"
                            className="w-full h-32 resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                        </div>

                        <div className="grid gap-3 sm:grid-cols-2">
                          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                            <p className="text-sm font-bold text-[#1e3a5f] mb-3">管辖法院</p>
                            <input value={formData.court_name} onChange={(e) => setFormData({...formData, court_name: e.target.value})} placeholder="XX市XX区人民法院"
                              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                          </div>
                          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                            <p className="text-sm font-bold text-[#1e3a5f] mb-3">法律依据（选填）</p>
                            <textarea value={formData.legal_basis} onChange={(e) => setFormData({...formData, legal_basis: e.target.value})} placeholder="相关法条"
                              className="w-full h-20 resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                          </div>
                        </div>

                        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                          <p className="text-sm font-bold text-[#1e3a5f] mb-3">证据清单（选填）</p>
                          <textarea value={formData.evidence_list} onChange={(e) => setFormData({...formData, evidence_list: e.target.value})} placeholder={"每行一项证据，例如：\n1. 劳动合同\n2. 工资流水\n3. 微信聊天记录"}
                            className="w-full h-24 resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-[#1e3a5f] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/10" />
                        </div>

                        <button onClick={handleGenerateLawsuitFromForm} disabled={lawsuitLoading}
                          className="w-full rounded-xl bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8a] py-3 font-semibold text-white transition-all hover:shadow-lg hover:shadow-[#1e3a5f]/15 disabled:opacity-50 flex items-center justify-center gap-2">
                          {lawsuitLoading ? <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                            : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
                          生成起诉状
                        </button>
                      </div>
                    )}

                {activeTab === 'calculator' && <CalculatorPanel />}
              </div>
            </div>
          </div>
        </main>

        <aside className="hidden lg:block lg:w-60 xl:w-72 flex-shrink-0 border-l border-slate-200/80 bg-white">
          <div className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <svg className="w-4 h-4 text-[#1e3a5f]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <p className="text-sm font-bold text-[#1e3a5f]">历史记录</p>
            </div>
            {!historyLoaded ? (
              <p className="text-xs text-slate-400 text-center py-8">加载中...</p>
            ) : history.length > 0 ? (
              <ul className="space-y-2">
                {history.map((item) => (
                  <li key={item.id} className="bg-slate-50 rounded-lg p-3 hover:bg-slate-100 transition-colors cursor-pointer group"
                    onClick={() => { setLawsuitInputId(item.id); setActiveTab('document'); addToast('已填入咨询ID', 'success'); }}>
                    <div className="text-sm font-medium text-slate-800 truncate">{item.query}</div>
                    <div className="text-[11px] text-slate-400 mt-1">{new Date(item.created_at).toLocaleDateString()}</div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-slate-400 text-center py-8">暂无咨询记录</p>
            )}
          </div>
        </aside>
      </div>

      <section className="border-t border-slate-200/80 bg-white">
        <div className="max-w-[1440px] mx-auto px-4 md:px-6 py-8">
          <div className="text-center mb-6">
            <h2 className="text-lg font-bold text-[#1e3a5f]">使用指南</h2>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((step) => (
              <div key={step.num} className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 hover:border-[#1e3a5f]/30 hover:shadow-md transition-all">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">{step.icon}</span>
                  <span className="text-[11px] font-bold text-[#d4a84b] uppercase">Step {step.num}</span>
                </div>
                <h3 className="text-sm font-bold text-[#1e3a5f] mb-1">{step.title}</h3>
                <p className="text-xs text-slate-500 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200/80 bg-white px-4 md:px-6 py-4">
        <div className="max-w-[1440px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Image src="/logo1.png" alt="法护星" width={18} height={18} className="w-4.5 h-4.5 rounded object-contain opacity-50" />
            <span className="text-xs text-slate-400">© {currentYear} 法护星</span>
          </div>
          <span className="text-xs text-slate-400">基于腾讯元器</span>
        </div>
      </footer>
    </div>
  );
}
