'use client';

import { useState } from 'react';
import { track } from '@/lib/tracker';
import { useI18n } from '@/lib/i18n';
import LanguageSelector from '@/components/LanguageSelector';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const PRACTICE_AREAS = [
  { key: 'mx_divorce', labelKey: 'help.caseTypes.mx_divorce' },
  { key: 'mx_consumer', labelKey: 'help.caseTypes.mx_consumer' },
  { key: 'mx_labor', labelKey: 'help.caseTypes.mx_labor' },
  { key: 'immigration', labelKey: 'help.caseTypes.immigration' },
  { key: 'tax_resolution', labelKey: 'help.caseTypes.tax_resolution' },
];

export default function OnboardTenantPage() {
  const { t } = useI18n();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    firm_name: '', admin_email: '', admin_password: '',
    practice_areas: [] as string[],
    disclaimer_en: 'This platform does not provide legal advice. All information is for operational purposes only.',
    disclaimer_es: 'Esta plataforma no proporciona asesor\u00eda legal. Toda la informaci\u00f3n es solo para fines operativos.',
  });
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const toggleArea = (key: string) => {
    setForm((prev) => ({
      ...prev,
      practice_areas: prev.practice_areas.includes(key)
        ? prev.practice_areas.filter((a) => a !== key)
        : [...prev.practice_areas, key],
    }));
  };

  const handleSubmit = async () => {
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_URL}/public/onboard`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) { const body = await res.json().catch(() => ({})); throw new Error(body.detail || `Error: ${res.status}`); }
      const data = await res.json();
      setResult(data); setStep(4);
      track('tenant_created', { firm_name: form.firm_name });
    } catch (err: any) {
      setError(err.message?.includes('fetch') ? t('errors.networkError') : (err.message || t('errors.submitFailed')));
    } finally { setLoading(false); }
  };

  if (step === 4 && result) {
    return (
      <div className="max-w-2xl mx-auto mt-16 p-8">
        <h1 className="text-3xl font-bold mb-6 text-green-700">{t('onboarding.step3Title')}</h1>
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="font-semibold mb-3">{t('onboarding.loginUrl')}</h2>
          <p className="text-sm"><strong>Email:</strong> {result.admin_email}</p>
          <p className="text-sm"><strong>Login:</strong> <a href={result.login_url} className="text-blue-600 underline">{result.login_url}</a></p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="font-semibold mb-3">{t('onboarding.embedSnippet')}</h2>
          <pre className="bg-gray-100 p-4 rounded text-xs overflow-x-auto whitespace-pre-wrap">{result.embed_snippet}</pre>
          <button onClick={() => navigator.clipboard.writeText(result.embed_snippet)}
            className="mt-3 px-4 py-2 bg-gray-800 text-white rounded text-sm hover:bg-gray-900">
            Copy
          </button>
        </div>
        <a href="/app/login" className="block text-center py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition">
          {t('onboarding.goToLogin')}
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto mt-16 p-8">
      <div className="flex justify-end mb-4"><LanguageSelector /></div>
      <h1 className="text-3xl font-bold mb-2">{t('onboarding.title')}</h1>
      <p className="text-gray-600 mb-6">{t('onboarding.subtitle')}</p>

      {error && <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm">{error}</div>}

      <div className="flex gap-2 mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className={`flex-1 h-2 rounded ${step >= s ? 'bg-blue-600' : 'bg-gray-200'}`} />
        ))}
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">{t('onboarding.step1Title')}</h2>
          <div>
            <label className="block text-sm font-medium mb-1">{t('onboarding.firmName')} *</label>
            <input required className="w-full border rounded-lg px-3 py-2.5"
              value={form.firm_name} onChange={(e) => setForm({ ...form, firm_name: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t('onboarding.adminEmail')} *</label>
            <input type="email" required className="w-full border rounded-lg px-3 py-2.5"
              value={form.admin_email} onChange={(e) => setForm({ ...form, admin_email: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t('onboarding.adminPassword')} *</label>
            <input type="password" required className="w-full border rounded-lg px-3 py-2.5"
              value={form.admin_password} onChange={(e) => setForm({ ...form, admin_password: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-3">{t('onboarding.practiceAreas')}</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {PRACTICE_AREAS.map((area) => (
                <button key={area.key} type="button" onClick={() => toggleArea(area.key)}
                  className={`px-4 py-3 rounded-lg border text-sm font-medium transition ${
                    form.practice_areas.includes(area.key) ? 'bg-blue-50 border-blue-500 text-blue-700' : 'bg-white border-gray-200 text-gray-600 hover:border-gray-400'
                  }`}>
                  {t(area.labelKey)}
                </button>
              ))}
            </div>
          </div>
          <button onClick={() => setStep(2)} disabled={!form.firm_name || !form.admin_email || !form.admin_password}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50">
            {t('onboarding.nextStep')}
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">{t('onboarding.step2Title')}</h2>
          <p className="text-sm text-gray-600">{t('onboarding.step2Desc')}</p>
          <div>
            <label className="block text-sm font-medium mb-1">{t('onboarding.disclaimerEs')}</label>
            <textarea rows={3} className="w-full border rounded-lg px-3 py-2 text-sm"
              value={form.disclaimer_es} onChange={(e) => setForm({ ...form, disclaimer_es: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t('onboarding.disclaimerEn')}</label>
            <textarea rows={3} className="w-full border rounded-lg px-3 py-2 text-sm"
              value={form.disclaimer_en} onChange={(e) => setForm({ ...form, disclaimer_en: e.target.value })} />
          </div>
          <div className="flex gap-3">
            <button onClick={() => setStep(1)} className="flex-1 py-3 bg-gray-200 rounded-lg">{t('onboarding.prevStep')}</button>
            <button onClick={() => setStep(3)} className="flex-1 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">
              {t('onboarding.nextStep')}
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">{t('onboarding.step3Title')}</h2>
          <div className="bg-gray-50 rounded-lg p-4 text-sm space-y-2">
            <p><strong>{t('onboarding.firmName')}:</strong> {form.firm_name}</p>
            <p><strong>{t('onboarding.adminEmail')}:</strong> {form.admin_email}</p>
            <p><strong>{t('onboarding.practiceAreas')}:</strong> {form.practice_areas.map((a) => t(`help.caseTypes.${a}`)).join(', ') || '-'}</p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => setStep(2)} className="flex-1 py-3 bg-gray-200 rounded-lg">{t('onboarding.prevStep')}</button>
            <button onClick={handleSubmit} disabled={loading}
              className="flex-1 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50">
              {loading ? t('common.loading') : t('onboarding.createFirm')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
