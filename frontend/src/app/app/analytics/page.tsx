'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

const VERTICALS = ['immigration', 'tax_resolution', 'mx_divorce', 'interpreter'];

export default function AnalyticsPage() {
  const [overview7, setOverview7] = useState<any>(null);
  const [overview30, setOverview30] = useState<any>(null);
  const [funnel, setFunnel] = useState<any>(null);
  const [selectedVertical, setSelectedVertical] = useState('immigration');
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadFunnel();
  }, [selectedVertical]);

  const loadData = async () => {
    try {
      const [o7, o30] = await Promise.all([
        api.getAnalyticsOverview(7),
        api.getAnalyticsOverview(30),
      ]);
      setOverview7(o7);
      setOverview30(o30);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const loadFunnel = async () => {
    try {
      const f = await api.getAnalyticsFunnel(selectedVertical, 30);
      setFunnel(f);
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (error) return <div className="text-red-600 p-4">{error}</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Analytics</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KPICard label="Intakes (7d)" value={overview7?.intakes_total} prev={overview30?.intakes_total} suffix=" (30d)" />
        <KPICard label="Matters (7d)" value={overview7?.matters_total} prev={overview30?.matters_total} suffix=" (30d)" />
        <KPICard label="Approvals Pending" value={overview7?.approvals_pending} />
        <KPICard label="Approvals Approved (7d)" value={overview7?.approvals_approved} prev={overview30?.approvals_approved} suffix=" (30d)" />
        <KPICard label="Approvals Rejected (7d)" value={overview7?.approvals_rejected} />
        <KPICard label="Time to Approve (med)" value={overview7?.time_to_approve_median_hours != null ? `${overview7.time_to_approve_median_hours}h` : 'N/A'} />
        <KPICard label="Leads (7d)" value={overview7?.leads_total} prev={overview30?.leads_total} suffix=" (30d)" />
        <KPICard label="Events (7d)" value={overview7?.events_total} prev={overview30?.events_total} suffix=" (30d)" />
      </div>

      {/* Funnel */}
      <section className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Conversion Funnel (30d)</h2>
          <div className="flex gap-2">
            {VERTICALS.map((v) => (
              <button key={v} onClick={() => setSelectedVertical(v)}
                className={`px-3 py-1 rounded text-sm ${selectedVertical === v ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}>
                {v.replace('_', ' ')}
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
          <p className="text-gray-500 text-sm">Loading funnel...</p>
        )}
      </section>

      {/* Drop-off table */}
      {funnel?.steps && (
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Top Drop-Off Steps</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Step Transition</th>
                <th className="pb-2">From</th>
                <th className="pb-2">To</th>
                <th className="pb-2">Drop-off</th>
              </tr>
            </thead>
            <tbody>
              {funnel.steps.slice(1)
                .map((step: any, i: number) => ({
                  from_name: funnel.steps[i].name,
                  to_name: step.name,
                  from_count: funnel.steps[i].count,
                  to_count: step.count,
                  dropoff: funnel.steps[i].count > 0
                    ? Math.round((1 - step.count / funnel.steps[i].count) * 100)
                    : 0,
                }))
                .sort((a: any, b: any) => b.dropoff - a.dropoff)
                .map((row: any, i: number) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-2">{row.from_name} &rarr; {row.to_name}</td>
                    <td className="py-2">{row.from_count}</td>
                    <td className="py-2">{row.to_count}</td>
                    <td className="py-2">
                      <span className={`font-medium ${row.dropoff > 50 ? 'text-red-600' : row.dropoff > 25 ? 'text-yellow-600' : 'text-green-600'}`}>
                        {row.dropoff}%
                      </span>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}

function KPICard({ label, value, prev, suffix }: { label: string; value: any; prev?: any; suffix?: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-bold">{value ?? '-'}</p>
      {prev != null && <p className="text-xs text-gray-400 mt-1">{prev}{suffix}</p>}
    </div>
  );
}
