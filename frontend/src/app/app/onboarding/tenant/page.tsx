'use client';

import { useState } from 'react';
import { track } from '@/lib/tracker';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const PRACTICE_AREAS = [
  { key: 'immigration', label: 'Immigration' },
  { key: 'tax_resolution', label: 'Tax Resolution' },
  { key: 'interpreter', label: 'Interpreter Services' },
  { key: 'mx_divorce', label: 'Divorcio Incausado (MX)' },
];

export default function OnboardTenantPage() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    firm_name: '',
    admin_email: '',
    admin_password: '',
    practice_areas: [] as string[],
    disclaimer_en: 'This platform does not provide legal advice. All information is for operational purposes only.',
    disclaimer_es: 'Esta plataforma no proporciona asesoría legal. Toda la información es solo para fines operativos.',
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
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/public/onboard`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Error: ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
      setStep(4);
      track('tenant_created', { firm_name: form.firm_name });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (step === 4 && result) {
    return (
      <div className="max-w-2xl mx-auto mt-16 p-8">
        <h1 className="text-3xl font-bold mb-6 text-green-700">You are set up!</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="font-semibold mb-3">Your Credentials</h2>
          <p className="text-sm"><strong>Email:</strong> {result.admin_email}</p>
          <p className="text-sm"><strong>Login:</strong> <a href={result.login_url} className="text-blue-600 underline">{result.login_url}</a></p>
          <p className="text-sm"><strong>Tenant ID:</strong> {result.tenant_id}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="font-semibold mb-3">Intake Widget (embed on your website)</h2>
          <p className="text-sm text-gray-600 mb-3">
            Copy this HTML snippet and paste it on your website to let clients
            submit intakes directly.
          </p>
          <pre className="bg-gray-100 p-4 rounded text-xs overflow-x-auto whitespace-pre-wrap">
            {result.embed_snippet}
          </pre>
          <button
            onClick={() => navigator.clipboard.writeText(result.embed_snippet)}
            className="mt-3 px-4 py-2 bg-gray-800 text-white rounded text-sm hover:bg-gray-900"
          >
            Copy Snippet
          </button>
        </div>

        <a href="/app/login" className="block text-center py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition">
          Go to Login
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto mt-16 p-8">
      <h1 className="text-3xl font-bold mb-2">Set Up Your Firm</h1>
      <p className="text-gray-600 mb-6">Get started in under 2 minutes.</p>

      {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>}

      {/* Progress */}
      <div className="flex gap-2 mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className={`flex-1 h-2 rounded ${step >= s ? 'bg-blue-600' : 'bg-gray-200'}`} />
        ))}
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Step 1: Firm Details</h2>
          <div>
            <label className="block text-sm font-medium mb-1">Firm Name *</label>
            <input required className="w-full border rounded-lg px-3 py-2"
              value={form.firm_name} onChange={(e) => setForm({ ...form, firm_name: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Admin Email *</label>
            <input type="email" required className="w-full border rounded-lg px-3 py-2"
              value={form.admin_email} onChange={(e) => setForm({ ...form, admin_email: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password *</label>
            <input type="password" required className="w-full border rounded-lg px-3 py-2"
              value={form.admin_password} onChange={(e) => setForm({ ...form, admin_password: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-3">Practice Areas</label>
            <div className="grid grid-cols-2 gap-3">
              {PRACTICE_AREAS.map((area) => (
                <button key={area.key} type="button"
                  onClick={() => toggleArea(area.key)}
                  className={`px-4 py-3 rounded-lg border text-sm font-medium transition ${
                    form.practice_areas.includes(area.key)
                      ? 'bg-blue-50 border-blue-500 text-blue-700'
                      : 'bg-white border-gray-200 text-gray-600 hover:border-gray-400'
                  }`}>
                  {area.label}
                </button>
              ))}
            </div>
          </div>
          <button onClick={() => setStep(2)} disabled={!form.firm_name || !form.admin_email || !form.admin_password}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50">
            Next
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Step 2: Disclaimers</h2>
          <p className="text-sm text-gray-600">
            These disclaimers appear on all client-facing outputs.
          </p>
          <div>
            <label className="block text-sm font-medium mb-1">Disclaimer (English)</label>
            <textarea rows={3} className="w-full border rounded-lg px-3 py-2 text-sm"
              value={form.disclaimer_en} onChange={(e) => setForm({ ...form, disclaimer_en: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Disclaimer (Espanol)</label>
            <textarea rows={3} className="w-full border rounded-lg px-3 py-2 text-sm"
              value={form.disclaimer_es} onChange={(e) => setForm({ ...form, disclaimer_es: e.target.value })} />
          </div>
          <div className="flex gap-3">
            <button onClick={() => setStep(1)} className="flex-1 py-3 bg-gray-200 rounded-lg">Back</button>
            <button onClick={() => setStep(3)} className="flex-1 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">Next</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Step 3: Confirm</h2>
          <div className="bg-gray-50 rounded-lg p-4 text-sm space-y-2">
            <p><strong>Firm:</strong> {form.firm_name}</p>
            <p><strong>Admin:</strong> {form.admin_email}</p>
            <p><strong>Areas:</strong> {form.practice_areas.join(', ') || 'None selected'}</p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => setStep(2)} className="flex-1 py-3 bg-gray-200 rounded-lg">Back</button>
            <button onClick={handleSubmit} disabled={loading}
              className="flex-1 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50">
              {loading ? 'Creating...' : 'Create My Firm'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
