'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { track, trackPageView } from '@/lib/tracker';

const DEMO_TENANT_ID = '00000000-0000-0000-0000-000000000001';

const CASE_TYPES = [
  { value: 'mx_divorce', label: 'Divorcio Incausado', desc: 'Divorcio express, custodia, pensión' },
  { value: 'mx_consumer', label: 'Queja de Consumidor', desc: 'PROFECO, CONDUSEF, proveedores' },
  { value: 'mx_labor', label: 'Asunto Laboral', desc: 'Despido, liquidación, IMSS' },
  { value: 'immigration', label: 'Inmigración (US)', desc: 'Visas, asilo, deportación' },
  { value: 'tax_resolution', label: 'Fiscal (US)', desc: 'IRS, impuestos atrasados' },
];

const ENTIDADES = [
  'Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche',
  'Chiapas', 'Chihuahua', 'Ciudad de México', 'Coahuila', 'Colima',
  'Durango', 'Estado de México', 'Guanajuato', 'Guerrero', 'Hidalgo',
  'Jalisco', 'Michoacán', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca',
  'Puebla', 'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa',
  'Sonora', 'Tabasco', 'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas',
];

export default function IntakePage() {
  const [form, setForm] = useState({
    full_name: '',
    phone: '',
    email: '',
    case_type: 'mx_divorce',
    description: '',
    language: 'es',
    urgency_notes: '',
    entidad_federativa: '',
  });
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [intakeId, setIntakeId] = useState('');

  useEffect(() => {
    trackPageView({ page: 'intake' });

    // Read tenant_id and UTM from query params
    const params = new URLSearchParams(window.location.search);
    const lang = params.get('lang');
    if (lang === 'en' || lang === 'es') {
      setForm((f) => ({ ...f, language: lang }));
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    track('intake_submitted', { case_type: form.case_type });

    try {
      const params = new URLSearchParams(window.location.search);
      const tenantId = params.get('tenant_id') || DEMO_TENANT_ID;

      const result = await api.createIntake({
        tenant_id: tenantId,
        channel: 'web',
        raw_payload: {
          ...form,
          nombre_completo: form.full_name,
          entidad_federativa: form.entidad_federativa,
          utm_source: params.get('utm_source') || '',
          utm_medium: params.get('utm_medium') || '',
          utm_campaign: params.get('utm_campaign') || '',
        },
      });
      setIntakeId(result.id);
      setSubmitted(true);
      track('intake_created', { intake_id: result.id, case_type: form.case_type });
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (submitted) {
    return (
      <div className="max-w-lg mx-auto mt-12 px-4 py-8 bg-white rounded-xl shadow-sm border">
        <div className="text-center mb-4">
          <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-2xl text-green-600">&#10003;</span>
          </div>
          <h2 className="text-xl font-bold text-green-700">Información Recibida</h2>
        </div>
        <p className="text-gray-600 text-sm text-center mb-2">
          Tu información ha sido recibida. Un miembro de nuestro equipo
          revisará tu caso y se pondrá en contacto contigo.
        </p>
        <p className="text-xs text-gray-400 text-center mb-4">Referencia: {intakeId}</p>
        <div className="bg-red-50 border border-red-200 p-3 rounded-lg text-xs text-red-700">
          Este envío no crea una relación abogado-cliente.
          No se ha proporcionado ni se proporcionará asesoría legal a través de este formulario.
        </div>
      </div>
    );
  }

  const isMX = form.case_type.startsWith('mx_');

  return (
    <div className="max-w-lg mx-auto px-4 py-6 sm:py-8">
      <h1 className="text-2xl sm:text-3xl font-bold mb-1">Nuevo Intake</h1>
      <p className="text-xs text-red-600 mb-5 bg-red-50 border border-red-200 p-2.5 rounded-lg">
        Este formulario recopila información para evaluación del caso.
        No constituye asesoría legal ni crea relación abogado-cliente.
      </p>

      {error && <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Nombre completo *</label>
          <input
            required
            className="w-full border rounded-lg px-3 py-2.5 text-sm"
            placeholder="Tu nombre legal completo"
            value={form.full_name}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium mb-1">Teléfono / WhatsApp *</label>
            <input
              required
              type="tel"
              className="w-full border rounded-lg px-3 py-2.5 text-sm"
              placeholder="+52 55 1234 5678"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Correo electrónico</label>
            <input
              type="email"
              className="w-full border rounded-lg px-3 py-2.5 text-sm"
              placeholder="tu@correo.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Tipo de caso *</label>
          <div className="grid grid-cols-1 gap-2">
            {CASE_TYPES.map((t) => (
              <button key={t.value} type="button"
                onClick={() => setForm({ ...form, case_type: t.value })}
                className={`text-left p-3 border rounded-xl transition ${
                  form.case_type === t.value
                    ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500'
                    : 'border-gray-200 hover:border-gray-300 active:bg-gray-50'
                }`}>
                <div className="font-medium text-sm">{t.label}</div>
                <div className="text-xs text-gray-500">{t.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {isMX && (
          <div>
            <label className="block text-sm font-medium mb-1">Entidad federativa</label>
            <select className="w-full border rounded-lg px-3 py-2.5 text-sm"
              value={form.entidad_federativa}
              onChange={(e) => setForm({ ...form, entidad_federativa: e.target.value })}>
              <option value="">Selecciona tu estado</option>
              {ENTIDADES.map((ent) => (
                <option key={ent} value={ent}>{ent}</option>
              ))}
            </select>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium mb-1">Idioma preferido</label>
            <select
              className="w-full border rounded-lg px-3 py-2.5 text-sm"
              value={form.language}
              onChange={(e) => setForm({ ...form, language: e.target.value })}>
              <option value="es">Espa&ntilde;ol</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Describe tu situación *</label>
          <textarea
            required
            rows={4}
            className="w-full border rounded-lg px-3 py-2.5 text-sm"
            placeholder="Ej: Quiero tramitar mi divorcio incausado, tenemos dos hijos menores..."
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Notas de urgencia (fechas de audiencia, plazos, detención)
          </label>
          <textarea
            rows={2}
            className="w-full border rounded-lg px-3 py-2.5 text-sm"
            placeholder="Ej: Tengo audiencia el 15 de marzo..."
            value={form.urgency_notes}
            onChange={(e) => setForm({ ...form, urgency_notes: e.target.value })}
          />
        </div>

        <button
          type="submit"
          className="w-full py-3.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition text-base">
          Enviar Intake
        </button>
      </form>
    </div>
  );
}
