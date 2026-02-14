'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import ApprovalQueue from '@/components/ApprovalQueue';

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<any[]>([]);
  const [filter, setFilter] = useState<'pending' | 'approved' | 'rejected' | ''>('pending');
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const data = await api.getApprovals(filter || undefined);
      setApprovals(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    load();
  }, [filter]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Human Approval Gate</h1>
        <div className="flex gap-2">
          {(['pending', 'approved', 'rejected', ''] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded text-sm ${
                filter === f ? 'bg-gray-800 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              {f || 'All'}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>}

      <p className="text-sm text-red-600 mb-4">
        All items below require review by a licensed attorney or authorized staff
        before they can be sent to clients.
      </p>

      <ApprovalQueue approvals={approvals} onUpdate={load} />
    </div>
  );
}
