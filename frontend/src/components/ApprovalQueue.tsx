'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

interface Props {
  approvals: any[];
  onUpdate: () => void;
}

export default function ApprovalQueue({ approvals, onUpdate }: Props) {
  const [processing, setProcessing] = useState<string | null>(null);
  const [notes, setNotes] = useState<Record<string, string>>({});

  const handleDecision = async (id: string, action: 'approve' | 'reject') => {
    setProcessing(id);
    try {
      if (action === 'approve') {
        await api.approveItem(id, notes[id]);
      } else {
        await api.rejectItem(id, notes[id]);
      }
      onUpdate();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setProcessing(null);
    }
  };

  if (approvals.length === 0) {
    return <p className="text-gray-500 text-sm">No items in the approval queue.</p>;
  }

  return (
    <div className="space-y-4">
      {approvals.map((a) => (
        <div
          key={a.id}
          className={`bg-white rounded-lg shadow p-4 border-l-4 ${
            a.status === 'pending' ? 'border-yellow-400' :
            a.status === 'approved' ? 'border-green-400' :
            'border-red-400'
          }`}
        >
          <div className="flex justify-between items-start mb-3">
            <div>
              <p className="font-medium text-sm">
                {a.object_type === 'agent_run' ? 'Agent Run' : 'Message Draft'}
              </p>
              <p className="text-xs text-gray-500">
                Object: {a.object_id?.slice(0, 8)}... | Matter: {a.matter_id?.slice(0, 8)}...
              </p>
              <p className="text-xs text-gray-400">
                Created: {new Date(a.created_at).toLocaleString()}
              </p>
            </div>
            <span className={`text-xs px-2 py-1 rounded font-semibold uppercase ${
              a.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
              a.status === 'approved' ? 'bg-green-100 text-green-700' :
              'bg-red-100 text-red-700'
            }`}>
              {a.status}
            </span>
          </div>

          {a.notes && (
            <p className="text-sm text-gray-600 mb-3 bg-gray-50 p-2 rounded">{a.notes}</p>
          )}

          {a.status === 'pending' && (
            <>
              <div className="mb-3">
                <input
                  type="text"
                  placeholder="Add review notes (optional)"
                  className="w-full border rounded px-3 py-2 text-sm"
                  value={notes[a.id] || ''}
                  onChange={(e) => setNotes({ ...notes, [a.id]: e.target.value })}
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleDecision(a.id, 'approve')}
                  disabled={processing === a.id}
                  className="px-4 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50"
                >
                  Approve
                </button>
                <button
                  onClick={() => handleDecision(a.id, 'reject')}
                  disabled={processing === a.id}
                  className="px-4 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700 disabled:opacity-50"
                >
                  Reject
                </button>
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
