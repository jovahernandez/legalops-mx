'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { track, trackPageView } from '@/lib/tracker';
import { useI18n } from '@/lib/i18n';
import LanguageSelector from '@/components/LanguageSelector';

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

const validatePhone = (phone: string) => /^\+?\d{10,15}$/.test(phone.replace(/[\s\-()]/g, ''));
const validateEmail = (email: string) => !email || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

export default function IntakePage() {
  const { t } = useI18n();
  const [form, setForm] = useState({
    full_name: '', phone: '', email: '', case_type: 'mx_divorce',
    description: '', language: 'es', urgency_notes: '', entidad_federativa: '',
  });
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [intakeId, setIntakeId] = useState('');
  const [consent, setConsent] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    trackPageView({ page: 'intake' });
    const params = new URLSearchParams(window.location.search);
    const lang = params.get('lang');
    if (lang === 'en' || lang === 'es') setForm((f) => ({ ...f, language: lang }));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setError('');
    const errs: Record<string, string> = {};
    if (!form.full_name) errs.full_name = t('validation.fieldRequired');
    if (!form.phone) errs.phone = t('validation.fieldRequired');
    else if (!validatePhone(form.phone)) errs.phone = t('validation.phoneInvalid');
    if (form.email && !validateEmail(form.email)) errs.email = t('validation.emailInvalid');
    if (!form.description) errs.description = t('validation.fieldRequired');
    if (!consent) errs.consent = t('validation.consentRequired');
    setFieldErrors(errs);
    if (Object.keys(errs).length > 0) return;

    track('intake_submitted', { case_type: form.case_type });
    try {
      const params = new URLSearchParams(window.location.search);
      const tenantId = params.get('tenant_id') || DEMO_TENANT_ID;
      const result = await api.createIntake({
        tenant_id: tenantId, channel: 'web',
        raw_payload: { ...form, nombre_completo: form.full_name,
          utm_source: params.get('utm_source') || '', utm_medium: params.get('utm_medium') || '',
        },
      });
      setIntakeId(result.id); setSubmitted(true);
      track('intake_created', { intake_id: result.id, case_type: form.case_type });
    } catch (err: any) {
      setError(err.message?.includes('fetch') ? t('errors.networkError') : (err.message || t('errors.submitFailed')));
    }
  };

  if (submitted) {
    return (
      <div className="max-w-lg mx-auto mt-12 px-4 py-8 bg-white rounded-xl shadow-sm border">
        <div className="text-center mb-4">
          <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-2xl text-green-600">&#10003;</span>
          </div>
          <h2 className="text-xl font-bold text-green-700">{t('intake.successTitle')}</h2>
        </div>
        <p className="text-gray-600 text-sm text-center mb-2">{t('intake.successMsg')}</p>
        <p className="text-xs text-gray-400 text-center mb-4">Ref: {intakeId}</p>
        <div className="bg-red-50 border border-red-200 p-3 rounded-lg text-xs text-red-700">{t('disclaimer.short')}</div>
      </div>
    );
  }

  const isMX = form.case_type.startsWith('mx_');
  const clearErr = (field: string) => setFieldErrors((prev) => ({ ...prev, [field]: '' }));

  return (
    <div className="max-w-lg mx-auto px-4 py-6 sm:py-8">
      <div className="flex justify-end mb-2"><LanguageSelector /></div>
      <h1 className="text-2xl sm:text-3xl font-bold mb-1">{t('intake.title')}</h1>
      <p className="text-xs text-red-600 mb-5 bg-red-50 border border-red-200 p-2.5 rounded-lg">{t('disclaimer.short')}</p>

      {error && <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">{t('intake.fullName')} *</label>
          <input required className={`w-full border rounded-lg px-3 py-2.5 text-sm ${fieldErrors.full_name ? 'border-red-400' : ''}`}
            value={form.full_name} onChange={(e) => { setForm({ ...form, full_name: e.target.value }); clearErr('full_name'); }} />
          {fieldErrors.full_name && <p className="text-red-500 text-xs mt-1">{fieldErrors.full_name}</p>}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium mb-1">{t('intake.whatsapp')} *</label>
            <input required type="tel" className={`w-full border rounded-lg px-3 py-2.5 text-sm ${fieldErrors.phone ? 'border-red-400' : ''}`}
              placeholder="+52 55 1234 5678"
              value={form.phone} onChange={(e) => { setForm({ ...form, phone: e.target.value }); clearErr('phone'); }} />
            <p className="text-xs text-gray-400 mt-0.5">{t('validation.phoneFormat')}</p>
            {fieldErrors.phone && <p className="text-red-500 text-xs mt-0.5">{fieldErrors.phone}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{t('intake.emailOptional')}</label>
            <input type="email" className={`w-full border rounded-lg px-3 py-2.5 text-sm ${fieldErrors.email ? 'border-red-400' : ''}`}
              value={form.email} onChange={(e) => { setForm({ ...form, email: e.target.value }); clearErr('email'); }} />
            {fieldErrors.email && <p className="text-red-500 text-xs mt-1">{fieldErrors.email}</p>}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">{t('intake.caseType')} *</label>
          <div className="grid grid-cols-1 gap-2">
            {CASE_TYPE_KEYS.map((key) => (
              <button key={key} type="button"
                onClick={() => setForm({ ...form, case_type: key })}
                className={`text-left p-3 border rounded-xl transition ${
                  form.case_type === key ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'
                }`}>
                <div className="font-medium text-sm">{t(`help.caseTypes.${key}`)}</div>
              </button>
            ))}
          </div>
        </div>

        {isMX && (
          <div>
            <label className="block text-sm font-medium mb-1">{t('intake.state')}</label>
            <select className="w-full border rounded-lg px-3 py-2.5 text-sm"
              value={form.entidad_federativa}
              onChange={(e) => setForm({ ...form, entidad_federativa: e.target.value })}>
              <option value="">{t('intake.selectState')}</option>
              {ENTIDADES.map((ent) => <option key={ent} value={ent}>{ent}</option>)}
            </select>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-1">{t('intake.description')} *</label>
          <textarea required rows={4} className={`w-full border rounded-lg px-3 py-2.5 text-sm ${fieldErrors.description ? 'border-red-400' : ''}`}
            placeholder={t('intake.descPlaceholder')}
            value={form.description} onChange={(e) => { setForm({ ...form, description: e.target.value }); clearErr('description'); }} />
          {fieldErrors.description && <p className="text-red-500 text-xs mt-1">{fieldErrors.description}</p>}
        </div>

        <div>
          <label className="flex items-start gap-2 text-sm cursor-pointer">
            <input type="checkbox" className="mt-0.5 w-4 h-4 accent-blue-600"
              checked={consent} onChange={(e) => { setConsent(e.target.checked); clearErr('consent'); }} />
            <span className={fieldErrors.consent ? 'text-red-600' : 'text-gray-600'}>
              {t('validation.consentLabel')}
            </span>
          </label>
          {fieldErrors.consent && <p className="text-red-500 text-xs mt-1">{fieldErrors.consent}</p>}
        </div>

        <button type="submit"
          className="w-full py-3.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
          {t('intake.submitBtn')}
        </button>
      </form>
    </div>
  );
}
