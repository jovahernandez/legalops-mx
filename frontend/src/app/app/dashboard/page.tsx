'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import MatterCard from '@/components/MatterCard';

export default function DashboardPage() {
  const [matters, setMatters] = useState<any[]>([]);
  const [intakes, setIntakes] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [showConvert, setShowConvert] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [m, i] = await Promise.all([api.getMatters(), api.getIntakes()]);
      setMatters(m);
      setIntakes(i.filter((x: any) => x.status === 'new'));
    } catch (err: any) {
      setError(err.message);
    }
  };

  const convertIntake = async (intake: any) => {
    try {
      const payload = intake.raw_payload_json || {};
      await api.createMatter({
        intake_id: intake.id,
        type: payload.case_type || 'other',
        jurisdiction: payload.case_type === 'mx_divorce' ? 'MX' : 'US',
        urgency_score: payload.urgency_notes ? 70 : 30,
      });
      setShowConvert(null);
      loadData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>}

      {/* Pending Intakes */}
      {intakes.length > 0 && (
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Pending Intakes ({intakes.length})</h2>
          <div className="space-y-3">
            {intakes.map((intake: any) => (
              <div key={intake.id} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">
                      {intake.raw_payload_json?.full_name || intake.raw_payload_json?.nombre_completo || 'Unknown'}
                    </p>
                    <p className="text-sm text-gray-600">
                      Type: {intake.raw_payload_json?.case_type || 'N/A'} | Channel: {intake.channel}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      {intake.raw_payload_json?.description || intake.raw_payload_json?.descripcion || ''}
                    </p>
                    {intake.raw_payload_json?.urgency_notes && (
                      <p className="text-sm text-red-600 mt-1">
                        Urgency: {intake.raw_payload_json.urgency_notes}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => convertIntake(intake)}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition"
                  >
                    Convert to Matter
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Active Matters */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Active Matters ({matters.length})</h2>
        {matters.length === 0 ? (
          <p className="text-gray-500">No matters yet. Convert an intake to get started.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {matters.map((matter: any) => (
              <Link key={matter.id} href={`/app/matters/${matter.id}`}>
                <MatterCard matter={matter} />
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
