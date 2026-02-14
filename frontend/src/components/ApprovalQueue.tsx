'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { useI18n } from '@/lib/i18n';

interface Props {
  approvals: any[];
  onUpdate: () => void;
}

export default function ApprovalQueue({ approvals, onUpdate }: Props) {
  const { t } = useI18n();
  const [processing, setProcessing] = useState<string | null>(null);
  const [notes, setNotes] = useState<Record<string, string>>({});

  const handleDecision = async (id: string, action: 'approve' | 'reject') => {
    setProcessing(id);
    try {
      if (action === 'approve') { await api.approveItem(id, notes[id]); }
      else { await api.rejectItem(id, notes[id]); }
      onUpdate();
    } catch (err: any) {
      alert(err.message);
    } finally { setProcessing(null); }
  };

  if (approvals.length === 0) {
    return <p className="text-gray-500 text-sm">{t('approvals.noApprovals')}</p>;
  }

  return (
    <div className="space-y-4">
      {approvals.map((a) => (
        <div key={a.id} className={`bg-white rounded-lg shadow-sm border-l-4 p-4 ${
          a.status === 'pending' ? 'border-yellow-400' :
          a.status === 'approved' ? 'border-green-400' : 'border-red-400'
        }`}>
          <div className="flex justify-between items-start mb-3">
            <div>
              <p className="font-medium text-sm">
                {a.object_type === 'agent_run' ? t('approvals.objectTypes.agent_run') : t('approvals.objectTypes.message_draft')}
              </p>
              <p className="text-xs text-gray-500">
                ID: {a.object_id?.slice(0, 8)}... | Matter: {a.matter_id?.slice(0, 8)}...
              </p>
            </div>
            <span className={`text-xs px-2 py-1 rounded font-semibold uppercase ${
              a.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
              a.status === 'approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>{a.status}</span>
          </div>

          {a.status === 'pending' && (
            <>
              <div className="mb-3">
                <input type="text" placeholder={t('approvals.reviewNotes')}
                  className="w-full border rounded px-3 py-2 text-sm"
                  value={notes[a.id] || ''}
                  onChange={(e) => setNotes({ ...notes, [a.id]: e.target.value })} />
              </div>
              <div className="flex gap-2">
                <button onClick={() => handleDecision(a.id, 'approve')} disabled={processing === a.id}
                  className="px-4 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50">
                  {t('approvals.approve')}
                </button>
                <button onClick={() => handleDecision(a.id, 'reject')} disabled={processing === a.id}
                  className="px-4 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700 disabled:opacity-50">
                  {t('approvals.reject')}
                </button>
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
