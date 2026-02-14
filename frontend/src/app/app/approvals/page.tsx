'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import ApprovalQueue from '@/components/ApprovalQueue';
import ErrorCard from '@/components/ErrorCard';

export default function ApprovalsPage() {
  const { t } = useI18n();
  const [approvals, setApprovals] = useState<any[]>([]);
  const [filter, setFilter] = useState<'pending' | 'approved' | 'rejected' | ''>('pending');
  const [error, setError] = useState(false);

  const load = async () => {
    try {
      setError(false);
      const data = await api.getApprovals(filter || undefined);
      setApprovals(data);
    } catch {
      setError(true);
    }
  };

  useEffect(() => { load(); }, [filter]);

  const filterMap: Record<string, string> = {
    pending: t('approvals.filters.pending'),
    approved: t('approvals.filters.approved'),
    rejected: t('approvals.filters.rejected'),
    '': t('approvals.filters.all'),
  };

  if (error) return <div className="py-12"><ErrorCard onRetry={load} /></div>;

  return (
    <div>
      <div className="flex flex-wrap justify-between items-center mb-6 gap-3">
        <h1 className="text-2xl font-bold">{t('approvals.title')}</h1>
        <div className="flex gap-2">
          {(['pending', 'approved', 'rejected', ''] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded text-sm ${
                filter === f ? 'bg-gray-800 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              {filterMap[f]}
            </button>
          ))}
        </div>
      </div>

      <p className="text-sm text-red-600 mb-4 bg-red-50 border border-red-200 p-3 rounded-lg">
        {t('approvals.subtitle')}
      </p>

      <ApprovalQueue approvals={approvals} onUpdate={load} />
    </div>
  );
}
