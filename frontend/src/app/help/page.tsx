'use client';

import { useEffect, useState } from 'react';
import { track, trackPageView } from '@/lib/tracker';
import { useI18n } from '@/lib/i18n';
import LanguageSelector from '@/components/LanguageSelector';
import FeedbackModal from '@/components/FeedbackModal';
import ErrorCard from '@/components/ErrorCard';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const DEMO_TENANT_ID = '00000000-0000-0000-0000-000000000001';

const CASE_TYPE_KEYS = ['mx_divorce', 'mx_consumer', 'mx_labor', 'immigration', 'tax_resolution'];

const ENTIDADES = [
  'Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche',
  'Chiapas', 'Chihuahua', 'Ciudad de M\u00e9xico', 'Coahuila', 'Colima',
  'Durango', 'Estado de M\u00e9xico', 'Guanajuato', 'Guerrero', 'Hidalgo',
  'Jalisco', 'Michoac\u00e1n', 'Morelos', 'Nayarit', 'Nuevo Le\u00f3n', 'Oaxaca',
  'Puebla', 'Quer\u00e9taro', 'Quintana Roo', 'San Luis Potos\u00ed', 'Sinaloa',
  'Sonora', 'Tabasco', 'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucat\u00e1n', 'Zacatecas',
];

export default function HelpPage() {
  const { t } = useI18n();
  const [currentStep, setCurrentStep] = useState(1);
  const [form, setForm] = useState({
    full_name: '', email: '', phone: '', case_type: '',
    description: '', language: 'es', entidad_federativa: '',
  });
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [checkedDocs, setCheckedDocs] = useState<Record<number, boolean>>({});

  useEffect(() => { trackPageView({ page: 'help_b2c' }); }, []);

  const handleStep1Next = () => {
    if (!form.case_type) { setError(t('errors.generic')); return; }
    setError(''); track('prepkit_step1_completed', { case_type: form.case_type }); setCurrentStep(2);
  };

  const handleStep2Next = () => {
    if (!form.description) { setError(t('errors.generic')); return; }
    setError(''); track('prepkit_step2_completed', { case_type: form.case_type }); setCurrentStep(3);
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.full_name || !form.phone) { setError(t('errors.generic')); return; }
    setLoading(true); setError('');
    try {
      const params = new URLSearchParams(window.location.search);
      const utm: Record<string, string> = {};
      for (const key of ['utm_source', 'utm_medium', 'utm_campaign']) {
        const val = params.get(key); if (val) utm[key] = val;
      }
      if (form.entidad_federativa) utm['entidad_federativa'] = form.entidad_federativa;

      const res = await fetch(`${API_URL}/public/prepkit`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_id: DEMO_TENANT_ID, ...form, utm }),
      });
      if (!res.ok) { const body = await res.json().catch(() => ({})); throw new Error(body.detail || `Error: ${res.status}`); }
      const data = await res.json();
      setResult(data); setCurrentStep(4);
      track('prepkit_generated', { intake_id: data.intake_id, case_type: form.case_type });
    } catch (err: any) {
      setError(err.message?.includes('fetch') ? t('errors.networkError') : (err.message || t('errors.submitFailed')));
    } finally { setLoading(false); }
  };

  const checkedCount = Object.values(checkedDocs).filter(Boolean).length;
  const totalDocs = result?.document_checklist?.length || 0;
  const progressPct = totalDocs > 0 ? Math.round((checkedCount / totalDocs) * 100) : 0;

  const StepIndicator = () => (
    <div className="flex items-center justify-center gap-1 mb-6">
      {[1, 2, 3, 4].map((s) => (
        <div key={s} className="flex items-center gap-1">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold ${
            s === currentStep ? 'bg-blue-600 text-white' :
            s < currentStep ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-400'
          }`}>{s < currentStep ? '\u2713' : s}</div>
          {s < 4 && <div className={`w-6 sm:w-10 h-0.5 ${s < currentStep ? 'bg-green-500' : 'bg-gray-200'}`} />}
        </div>
      ))}
    </div>
  );

  if (currentStep === 4 && result) {
    return (
      <div className="max-w-lg mx-auto px-4 py-6 sm:py-8">
        <div className="flex justify-end mb-2"><LanguageSelector /></div>
        <StepIndicator />
        <h1 className="text-2xl sm:text-3xl font-bold mb-1">{t('help.resultTitle')}</h1>
        <p className="text-sm text-gray-500 mb-4">{t('help.resultDesc')}</p>

        <div className="bg-red-50 border border-red-200 p-3 rounded-lg mb-5 text-xs text-red-700">{t('disclaimer.text')}</div>

        <section className="bg-white rounded-lg shadow-sm border p-4 sm:p-6 mb-4">
          <h2 className="text-base font-semibold mb-2">{t('help.docsTitle')}</h2>
          <ul className="space-y-2">
            {result.document_checklist.map((doc: string, i: number) => (
              <li key={i} className="flex items-start gap-3">
                <input type="checkbox" className="mt-0.5 w-5 h-5 accent-green-600"
                  checked={!!checkedDocs[i]}
                  onChange={() => setCheckedDocs({ ...checkedDocs, [i]: !checkedDocs[i] })} />
                <span className={`text-sm ${checkedDocs[i] ? 'line-through text-gray-400' : ''}`}>{doc}</span>
              </li>
            ))}
          </ul>
          <div className="mt-3 bg-gray-100 rounded-full h-2.5">
            <div className="bg-green-500 h-2.5 rounded-full transition-all" style={{ width: `${progressPct}%` }} />
          </div>
          <p className="text-xs text-gray-400 mt-1">{checkedCount} / {totalDocs} {t('help.progress')}</p>
        </section>

        <section className="bg-white rounded-lg shadow-sm border p-4 sm:p-6 mb-4">
          <h2 className="text-base font-semibold mb-2">{t('help.questionsTitle')}</h2>
          <ol className="space-y-2">
            {result.questions_for_attorney.map((q: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="text-blue-500 font-semibold shrink-0">{i + 1}.</span>
                <span>{q}</span>
              </li>
            ))}
          </ol>
        </section>

        <button onClick={() => { setCurrentStep(1); setResult(null); setCheckedDocs({}); }}
          className="w-full py-3 bg-gray-100 text-gray-600 rounded-lg font-medium hover:bg-gray-200 transition text-sm mb-4">
          {t('help.startOver')}
        </button>

        {showFeedback && <FeedbackModal page="/help" onClose={() => setShowFeedback(false)} />}
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-6 sm:py-8">
      <div className="flex justify-end mb-2"><LanguageSelector /></div>
      <StepIndicator />

      <div className="bg-red-50 border border-red-200 p-3 rounded-lg mb-4 text-xs text-red-700">
        {t('disclaimer.short')}
      </div>

      <h1 className="text-2xl sm:text-3xl font-bold mb-1">{t('help.title')}</h1>
      <p className="text-gray-500 text-sm mb-5">{t('help.subtitle')}</p>

      {error && (
        error.includes(t('errors.networkError')) ?
          <ErrorCard message={error} onRetry={() => setError('')} /> :
          <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm">{error}</div>
      )}

      {currentStep === 1 && (
        <div className="space-y-4">
          <h2 className="text-base font-semibold">{t('help.step1Title')}</h2>
          <div className="grid grid-cols-1 gap-2">
            {CASE_TYPE_KEYS.map((key) => (
              <button key={key} type="button"
                onClick={() => { setForm({ ...form, case_type: key }); setError(''); }}
                className={`text-left p-3.5 border rounded-xl transition ${
                  form.case_type === key ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'
                }`}>
                <div className="font-medium text-sm">{t(`help.caseTypes.${key}`)}</div>
              </button>
            ))}
          </div>
          <button type="button" onClick={handleStep1Next}
            className="w-full py-3.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
            {t('common.next')} &rarr;
          </button>
        </div>
      )}

      {currentStep === 2 && (
        <div className="space-y-4">
          <h2 className="text-base font-semibold">{t('help.step2Title')}</h2>
          <div>
            <label className="block text-sm font-medium mb-1">{t('help.situationLabel')} *</label>
            <textarea required rows={4} className="w-full border rounded-lg px-3 py-2.5 text-sm"
              placeholder={t('help.situationPlaceholder')}
              value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          {form.case_type.startsWith('mx_') && (
            <div>
              <label className="block text-sm font-medium mb-1">{t('help.state')}</label>
              <select className="w-full border rounded-lg px-3 py-2.5 text-sm"
                value={form.entidad_federativa}
                onChange={(e) => setForm({ ...form, entidad_federativa: e.target.value })}>
                <option value="">{t('help.selectState')}</option>
                {ENTIDADES.map((e) => <option key={e} value={e}>{e}</option>)}
              </select>
            </div>
          )}
          <div className="flex gap-3">
            <button type="button" onClick={() => setCurrentStep(1)}
              className="flex-1 py-3 bg-gray-100 text-gray-600 rounded-lg font-medium hover:bg-gray-200 transition">
              &larr; {t('common.back')}
            </button>
            <button type="button" onClick={handleStep2Next}
              className="flex-1 py-3.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
              {t('common.next')} &rarr;
            </button>
          </div>
        </div>
      )}

      {currentStep === 3 && (
        <form onSubmit={handleGenerate} className="space-y-4">
          <h2 className="text-base font-semibold">{t('help.step3Title')}</h2>
          <div>
            <label className="block text-sm font-medium mb-1">{t('help.fullName')} *</label>
            <input required className="w-full border rounded-lg px-3 py-2.5 text-sm"
              value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t('help.whatsapp')} *</label>
            <input required type="tel" className="w-full border rounded-lg px-3 py-2.5 text-sm"
              placeholder="+52 55 1234 5678"
              value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t('help.emailOptional')}</label>
            <input type="email" className="w-full border rounded-lg px-3 py-2.5 text-sm"
              value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t('help.preferredLang')}</label>
            <select className="w-full border rounded-lg px-3 py-2.5 text-sm"
              value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })}>
              <option value="es">Espa&ntilde;ol</option>
              <option value="en">English</option>
            </select>
          </div>
          <div className="flex gap-3">
            <button type="button" onClick={() => setCurrentStep(2)}
              className="flex-1 py-3 bg-gray-100 text-gray-600 rounded-lg font-medium hover:bg-gray-200 transition">
              &larr; {t('common.back')}
            </button>
            <button type="submit" disabled={loading}
              className="flex-1 py-3.5 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50">
              {loading ? t('common.loading') : t('help.submitBtn')}
            </button>
          </div>
        </form>
      )}

      {showFeedback && <FeedbackModal page="/help" onClose={() => setShowFeedback(false)} />}
    </div>
  );
}
