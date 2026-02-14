'use client';

import { useEffect, useState } from 'react';
import { track, trackPageView, getAnonymousId } from '@/lib/tracker';
import FeedbackModal from '@/components/FeedbackModal';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const DEMO_TENANT_ID = '00000000-0000-0000-0000-000000000001';

const CASE_TYPES = [
  { value: 'mx_divorce', label: 'Divorcio Incausado', desc: 'Divorcio express, custodia, pensión alimenticia, bienes' },
  { value: 'mx_consumer', label: 'Queja de Consumidor', desc: 'Problemas con proveedores, bancos, PROFECO, CONDUSEF' },
  { value: 'mx_labor', label: 'Asunto Laboral', desc: 'Despido, liquidación, salarios, IMSS, prestaciones' },
  { value: 'immigration', label: 'Inmigración (US)', desc: 'Visas, asilo, defensa deportación, green cards' },
];

const ENTIDADES = [
  'Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche',
  'Chiapas', 'Chihuahua', 'Ciudad de México', 'Coahuila', 'Colima',
  'Durango', 'Estado de México', 'Guanajuato', 'Guerrero', 'Hidalgo',
  'Jalisco', 'Michoacán', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca',
  'Puebla', 'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa',
  'Sonora', 'Tabasco', 'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas',
];

export default function HelpPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    case_type: '',
    description: '',
    language: 'es',
    entidad_federativa: '',
  });
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [checkedDocs, setCheckedDocs] = useState<Record<number, boolean>>({});

  useEffect(() => {
    trackPageView({ page: 'help_b2c' });
  }, []);

  const handleStep1Next = () => {
    if (!form.case_type) {
      setError('Selecciona un tipo de caso.');
      return;
    }
    setError('');
    track('prepkit_step1_completed', { case_type: form.case_type });
    setCurrentStep(2);
  };

  const handleStep2Next = () => {
    if (!form.description) {
      setError('Describe brevemente tu situación.');
      return;
    }
    setError('');
    track('prepkit_step2_completed', { case_type: form.case_type });
    setCurrentStep(3);
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.full_name) {
      setError('Ingresa tu nombre completo.');
      return;
    }
    if (!form.phone) {
      setError('Ingresa tu teléfono o WhatsApp.');
      return;
    }
    setLoading(true);
    setError('');
    track('prepkit_started', { case_type: form.case_type });

    try {
      const params = new URLSearchParams(window.location.search);
      const utm: Record<string, string> = {};
      for (const key of ['utm_source', 'utm_medium', 'utm_campaign']) {
        const val = params.get(key);
        if (val) utm[key] = val;
      }
      if (form.entidad_federativa) {
        utm['entidad_federativa'] = form.entidad_federativa;
      }

      const res = await fetch(`${API_URL}/public/prepkit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: DEMO_TENANT_ID,
          ...form,
          utm,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Error: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
      setCurrentStep(4);
      track('prepkit_generated', { intake_id: data.intake_id, case_type: form.case_type });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleContactFirm = async () => {
    try {
      const params = new URLSearchParams(window.location.search);
      const utm: Record<string, string> = {};
      for (const key of ['utm_source', 'utm_medium', 'utm_campaign']) {
        const val = params.get(key);
        if (val) utm[key] = val;
      }

      await fetch(`${API_URL}/public/lead`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_type: 'b2c_prepkit',
          vertical: form.case_type,
          contact: {
            name: form.full_name,
            email: form.email,
            phone: form.phone,
            entidad_federativa: form.entidad_federativa,
          },
          utm,
        }),
      });
      track('lead_created', { vertical: form.case_type, source: 'prepkit' });
      alert('Un despacho asociado se pondrá en contacto contigo. ¡Gracias!');
    } catch {
      alert('Error al enviar. Intenta de nuevo.');
    }
  };

  const checkedCount = Object.values(checkedDocs).filter(Boolean).length;
  const totalDocs = result?.document_checklist?.length || 0;
  const progressPct = totalDocs > 0 ? Math.round((checkedCount / totalDocs) * 100) : 0;

  // Step indicator
  const StepIndicator = () => (
    <div className="flex items-center justify-center gap-1 mb-6">
      {[1, 2, 3, 4].map((s) => (
        <div key={s} className="flex items-center gap-1">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold ${
            s === currentStep ? 'bg-blue-600 text-white' :
            s < currentStep ? 'bg-green-500 text-white' :
            'bg-gray-200 text-gray-400'
          }`}>
            {s < currentStep ? '\u2713' : s}
          </div>
          {s < 4 && <div className={`w-6 sm:w-10 h-0.5 ${s < currentStep ? 'bg-green-500' : 'bg-gray-200'}`} />}
        </div>
      ))}
    </div>
  );

  // STEP 4: Results
  if (currentStep === 4 && result) {
    return (
      <div className="max-w-lg mx-auto px-4 py-6 sm:py-8">
        <StepIndicator />
        <h1 className="text-2xl sm:text-3xl font-bold mb-1">Tu Prep Kit</h1>
        <p className="text-sm text-gray-500 mb-4">Expediente preparado para revisión profesional</p>

        <div className="bg-red-50 border border-red-200 p-3 rounded-lg mb-5 text-xs text-red-700">
          {result.disclaimer}
        </div>

        <section className="bg-white rounded-lg shadow-sm border p-4 sm:p-6 mb-4">
          <h2 className="text-base font-semibold mb-2">Documentos a Reunir</h2>
          <p className="text-xs text-gray-400 mb-3">
            Checklist general. Tu abogado puede solicitar documentos adicionales.
          </p>
          <ul className="space-y-2">
            {result.document_checklist.map((doc: string, i: number) => (
              <li key={i} className="flex items-start gap-3">
                <input
                  type="checkbox"
                  className="mt-0.5 w-5 h-5 accent-green-600"
                  checked={!!checkedDocs[i]}
                  onChange={() => setCheckedDocs({ ...checkedDocs, [i]: !checkedDocs[i] })}
                />
                <span className={`text-sm ${checkedDocs[i] ? 'line-through text-gray-400' : ''}`}>{doc}</span>
              </li>
            ))}
          </ul>
          <div className="mt-3 bg-gray-100 rounded-full h-2.5">
            <div
              className="bg-green-500 h-2.5 rounded-full transition-all"
              style={{ width: `${progressPct}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-1">{checkedCount} de {totalDocs} documentos listos</p>
        </section>

        <section className="bg-white rounded-lg shadow-sm border p-4 sm:p-6 mb-4">
          <h2 className="text-base font-semibold mb-2">Preguntas para tu Abogado</h2>
          <p className="text-xs text-gray-400 mb-3">
            Preguntas informativas para discutir con un profesional. NO es asesoría legal.
          </p>
          <ol className="space-y-2">
            {result.questions_for_attorney.map((q: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="text-blue-500 font-semibold shrink-0">{i + 1}.</span>
                <span>{q}</span>
              </li>
            ))}
          </ol>
        </section>

        <section className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 sm:p-6 mb-4">
          <h2 className="text-base font-semibold mb-1">Resumen de tu Caso</h2>
          <p className="text-sm text-yellow-800">
            Tu expediente ha sido generado y está <strong>pendiente de revisión
            por un profesional con cédula</strong>. Te contactaremos cuando la revisión esté completa.
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Estado: {result.case_packet_status} | Ref: {result.intake_id?.slice(0, 8)}...
          </p>
        </section>

        <button onClick={handleContactFirm}
          className="w-full py-3.5 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition text-base mb-3">
          Contactar Despacho Asociado
        </button>
        <button onClick={() => { setCurrentStep(1); setResult(null); setCheckedDocs({}); setForm({ ...form, description: '', case_type: '', entidad_federativa: '' }); }}
          className="w-full py-3 bg-gray-100 text-gray-600 rounded-lg font-medium hover:bg-gray-200 transition text-sm mb-4">
          Comenzar de nuevo
        </button>

        <div className="text-center">
          <button onClick={() => setShowFeedback(true)}
            className="text-xs text-gray-400 hover:text-gray-600 underline">
            Enviar comentarios sobre este Prep Kit
          </button>
        </div>

        {showFeedback && <FeedbackModal page="/help" onClose={() => setShowFeedback(false)} />}
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-6 sm:py-8">
      <StepIndicator />

      {/* Disclaimer above fold */}
      <div className="bg-red-50 border border-red-200 p-3 rounded-lg mb-4 text-xs text-red-700">
        Esta herramienta NO proporciona asesoría legal. No se crea relación abogado-cliente.
      </div>

      <h1 className="text-2xl sm:text-3xl font-bold mb-1">Prep Kit Legal Gratuito</h1>
      <p className="text-gray-500 text-sm mb-5">
        Obtén un checklist de documentos personalizado y preguntas para discutir con tu abogado.
      </p>

      {error && <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm">{error}</div>}

      {/* STEP 1: Select case type */}
      {currentStep === 1 && (
        <div className="space-y-4">
          <h2 className="text-base font-semibold">Paso 1: Tipo de caso</h2>
          <div className="grid grid-cols-1 gap-2">
            {CASE_TYPES.map((t) => (
              <button key={t.value} type="button"
                onClick={() => { setForm({ ...form, case_type: t.value }); setError(''); }}
                className={`text-left p-3.5 border rounded-xl transition ${
                  form.case_type === t.value
                    ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500'
                    : 'border-gray-200 hover:border-gray-300 active:bg-gray-50'
                }`}>
                <div className="font-medium text-sm">{t.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{t.desc}</div>
              </button>
            ))}
          </div>

          <button type="button" onClick={handleStep1Next}
            className="w-full py-3.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition text-base">
            Continuar &rarr;
          </button>
        </div>
      )}

      {/* STEP 2: Describe situation + location */}
      {currentStep === 2 && (
        <div className="space-y-4">
          <h2 className="text-base font-semibold">Paso 2: Tu situación</h2>

          <div>
            <label className="block text-sm font-medium mb-1">Describe brevemente tu situación *</label>
            <textarea required rows={4} className="w-full border rounded-lg px-3 py-2.5 text-sm"
              placeholder="Ej: Quiero solicitar el divorcio incausado, tenemos dos hijos menores..."
              value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>

          {form.case_type.startsWith('mx_') && (
            <div>
              <label className="block text-sm font-medium mb-1">Entidad federativa</label>
              <select className="w-full border rounded-lg px-3 py-2.5 text-sm"
                value={form.entidad_federativa}
                onChange={(e) => setForm({ ...form, entidad_federativa: e.target.value })}>
                <option value="">Selecciona tu estado</option>
                {ENTIDADES.map((e) => (
                  <option key={e} value={e}>{e}</option>
                ))}
              </select>
            </div>
          )}

          <div className="flex gap-3">
            <button type="button" onClick={() => { setCurrentStep(1); track('prepkit_step2_back', {}); }}
              className="flex-1 py-3 bg-gray-100 text-gray-600 rounded-lg font-medium hover:bg-gray-200 transition">
              &larr; Atrás
            </button>
            <button type="button" onClick={handleStep2Next}
              className="flex-1 py-3.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
              Continuar &rarr;
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Contact info + submit */}
      {currentStep === 3 && (
        <form onSubmit={handleGenerate} className="space-y-4">
          <h2 className="text-base font-semibold">Paso 3: Tus datos</h2>
          <p className="text-xs text-gray-500">
            Tu nombre y teléfono son necesarios para generar el Prep Kit.
            Te contactaremos cuando un profesional revise tu caso.
          </p>

          <div>
            <label className="block text-sm font-medium mb-1">Nombre completo *</label>
            <input required className="w-full border rounded-lg px-3 py-2.5 text-sm"
              placeholder="Tu nombre legal completo"
              value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Teléfono / WhatsApp *</label>
            <input required className="w-full border rounded-lg px-3 py-2.5 text-sm"
              type="tel"
              placeholder="+52 55 1234 5678"
              value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Correo electrónico (opcional)</label>
            <input type="email" className="w-full border rounded-lg px-3 py-2.5 text-sm"
              placeholder="tu@correo.com"
              value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Idioma preferido</label>
            <select className="w-full border rounded-lg px-3 py-2.5 text-sm"
              value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })}>
              <option value="es">Espa&ntilde;ol</option>
              <option value="en">English</option>
            </select>
          </div>

          <div className="flex gap-3">
            <button type="button" onClick={() => { setCurrentStep(2); track('prepkit_step3_back', {}); }}
              className="flex-1 py-3 bg-gray-100 text-gray-600 rounded-lg font-medium hover:bg-gray-200 transition">
              &larr; Atrás
            </button>
            <button type="submit" disabled={loading}
              className="flex-1 py-3.5 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50">
              {loading ? 'Generando...' : 'Obtener Prep Kit Gratis'}
            </button>
          </div>
        </form>
      )}

      <div className="mt-6 text-center">
        <button onClick={() => setShowFeedback(true)}
          className="text-xs text-gray-400 hover:text-gray-600 underline">
          Enviar comentarios
        </button>
      </div>

      {showFeedback && <FeedbackModal page="/help" onClose={() => setShowFeedback(false)} />}
    </div>
  );
}
