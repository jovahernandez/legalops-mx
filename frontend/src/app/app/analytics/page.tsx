'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import ErrorCard from '@/components/ErrorCard';
import { SkeletonKPI } from '@/components/Skeleton';

const VERTICALS = ['mx_divorce', 'mx_consumer', 'mx_labor', 'immigration', 'tax_resolution'];

export default function AnalyticsPage() {
  const { t } = useI18n();
  const [overview7, setOverview7] = useState<any>(null);
  const [overview30, setOverview30] = useState<any>(null);
  const [funnel, setFunnel] = useState<any>(null);
  const [selectedVertical, setSelectedVertical] = useState('mx_divorce');
  const [error, setError] = useState(false);

  const loadData = async () => {
    try {
      setError(false);
      const [o7, o30] = await Promise.all([
        api.getAnalyticsOverview(7),
        api.getAnalyticsOverview(30),
      ]);
      setOverview7(o7);
      setOverview30(o30);
    } catch {
      setError(true);
    }
  };

  const loadFunnel = async () => {
    try {
      const f = await api.getAnalyticsFunnel(selectedVertical, 30);
      setFunnel(f);
    } catch {
      // non-critical
    }
  };

  useEffect(() => { loadData(); }, []);
  useEffect(() => { loadFunnel(); }, [selectedVertical]);

  if (error) return <div className="py-12"><ErrorCard onRetry={loadData} /></div>;

  if (!overview7) {
    return (
      <div>
        <h1 className="text-2xl font-bold mb-6">{t('analytics.title')}</h1>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5].map((i) => <SkeletonKPI key={i} />)}
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">{t('analytics.title')}</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KPICard label={`${t('analytics.kpis.intakes')} (7d)`} value={overview7?.intakes_total} prev={overview30?.intakes_total} suffix=" (30d)" />
        <KPICard label={`${t('analytics.kpis.matters')} (7d)`} value={overview7?.matters_total} prev={overview30?.matters_total} suffix=" (30d)" />
        <KPICard label={t('analytics.kpis.approvals')} value={overview7?.approvals_pending} />
        <KPICard label={`${t('analytics.kpis.leads')} (7d)`} value={overview7?.leads_total} prev={overview30?.leads_total} suffix=" (30d)" />
        <KPICard label={`${t('analytics.kpis.events')} (7d)`} value={overview7?.events_total} prev={overview30?.events_total} suffix=" (30d)" />
      </div>

      <section className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <div className="flex flex-wrap justify-between items-center mb-4 gap-3">
          <h2 className="text-lg font-semibold">{t('analytics.funnel.title')} (30d)</h2>
          <div className="flex flex-wrap gap-2">
            {VERTICALS.map((v) => (
              <button key={v} onClick={() => setSelectedVertical(v)}
                className={`px-3 py-1 rounded text-xs ${selectedVertical === v ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
                {t(`leads.verticals.${v}`)}
              </button>
            ))}
          </div>
        </div>

        {funnel?.steps ? (
          <div className="space-y-3">
            {funnel.steps.map((step: any, i: number) => {
              const maxCount = Math.max(...funnel.steps.map((s: any) => s.count), 1);
              const width = Math.max((step.count / maxCount) * 100, 4);
              return (
                <div key={i}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">{step.name}</span>
                    <span>
                      {step.count}
                      {step.conversion_from_previous != null && (
                        <span className={`ml-2 text-xs ${step.conversion_from_previous >= 50 ? 'text-green-600' : 'text-red-600'}`}>
                          ({step.conversion_from_previous}%)
                        </span>
                      )}
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 rounded h-6">
                    <div className="bg-blue-500 rounded h-6 transition-all" style={{ width: `${width}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">{t('common.loading')}</p>
        )}
      </section>
    </div>
  );
}

function KPICard({ label, value, prev, suffix }: { label: string; value: any; prev?: any; suffix?: string }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-bold">{value ?? '-'}</p>
      {prev != null && <p className="text-xs text-gray-400 mt-1">{prev}{suffix}</p>}
    </div>
  );
}
