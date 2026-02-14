'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import MatterCard from '@/components/MatterCard';
import { useI18n } from '@/lib/i18n';
import ErrorCard from '@/components/ErrorCard';

export default function DashboardPage() {
  const { t } = useI18n();
  const [matters, setMatters] = useState<any[]>([]);
  const [intakes, setIntakes] = useState<any[]>([]);
  const [error, setError] = useState(false);

  const loadData = async () => {
    try {
      setError(false);
      const [m, i] = await Promise.all([api.getMatters(), api.getIntakes()]);
      setMatters(m);
      setIntakes(i.filter((x: any) => x.status === 'new'));
    } catch {
      setError(true);
    }
  };

  useEffect(() => { loadData(); }, []);

  const convertIntake = async (intake: any) => {
    try {
      const payload = intake.raw_payload_json || {};
      await api.createMatter({
        intake_id: intake.id,
        type: payload.case_type || 'other',
        jurisdiction: payload.case_type?.startsWith('mx_') ? 'MX' : 'US',
        urgency_score: payload.urgency_notes ? 70 : 30,
      });
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (error) return <div className="py-12"><ErrorCard onRetry={loadData} /></div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">{t('dashboard.title')}</h1>

      {intakes.length > 0 && (
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-3">{t('dashboard.pendingIntakes')} ({intakes.length})</h2>
          <div className="space-y-3">
            {intakes.map((intake: any) => (
              <div key={intake.id} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">
                      {intake.raw_payload_json?.full_name || intake.raw_payload_json?.nombre_completo || '-'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {t('common.type')}: {intake.raw_payload_json?.case_type || 'N/A'} | {intake.channel}
                    </p>
                    {intake.raw_payload_json?.urgency_notes && (
                      <p className="text-sm text-red-600 mt-1">
                        {t('dashboard.urgencyScore')}: {intake.raw_payload_json.urgency_notes}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => convertIntake(intake)}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition shrink-0"
                  >
                    {t('dashboard.convertToMatter')}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="text-lg font-semibold mb-3">{t('dashboard.activeMatters')} ({matters.length})</h2>
        {matters.length === 0 ? (
          <p className="text-gray-500">{t('dashboard.noMatters')}</p>
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
