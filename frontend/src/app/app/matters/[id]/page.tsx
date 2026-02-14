'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import DocumentUploader from '@/components/DocumentUploader';
import TaskList from '@/components/TaskList';
import AgentRunPanel from '@/components/AgentRunPanel';
import MessageDraftEditor from '@/components/MessageDraftEditor';

type Tab = 'overview' | 'documents' | 'tasks' | 'agents' | 'approvals' | 'messages';

export default function MatterDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [matter, setMatter] = useState<any>(null);
  const [tab, setTab] = useState<Tab>('overview');
  const [error, setError] = useState('');

  useEffect(() => {
    api.getMatter(id).then(setMatter).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <div className="text-red-600 p-4">{error}</div>;
  if (!matter) return <div className="p-4">Loading...</div>;

  const tabs: { key: Tab; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'documents', label: 'Documents' },
    { key: 'tasks', label: 'Tasks' },
    { key: 'agents', label: 'Agent Runs' },
    { key: 'approvals', label: 'Approvals' },
    { key: 'messages', label: 'Messages' },
  ];

  const urgencyColor =
    matter.urgency_score >= 70 ? 'text-red-600' :
    matter.urgency_score >= 40 ? 'text-yellow-600' : 'text-green-600';

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold">
          Matter: {matter.type.replace('_', ' ').toUpperCase()}
        </h1>
        <div className="flex gap-4 text-sm text-gray-600 mt-1">
          <span>ID: {matter.id.slice(0, 8)}...</span>
          <span>Jurisdiction: {matter.jurisdiction}</span>
          <span className={urgencyColor}>Urgency: {matter.urgency_score}/100</span>
          <span>Status: {matter.status}</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b mb-6">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              tab === t.key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'overview' && <OverviewTab matter={matter} />}
      {tab === 'documents' && <DocumentUploader matterId={id} />}
      {tab === 'tasks' && <TaskList matterId={id} />}
      {tab === 'agents' && <AgentRunPanel matterId={id} />}
      {tab === 'approvals' && <ApprovalsTab matterId={id} />}
      {tab === 'messages' && <MessageDraftEditor matterId={id} />}
    </div>
  );
}

function OverviewTab({ matter }: { matter: any }) {
  return (
    <div className="bg-white rounded-lg p-6 shadow">
      <h3 className="font-semibold mb-4">Case Summary</h3>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Type:</span>{' '}
          <span className="font-medium">{matter.type}</span>
        </div>
        <div>
          <span className="text-gray-500">Jurisdiction:</span>{' '}
          <span className="font-medium">{matter.jurisdiction}</span>
        </div>
        <div>
          <span className="text-gray-500">Status:</span>{' '}
          <span className="font-medium">{matter.status}</span>
        </div>
        <div>
          <span className="text-gray-500">Urgency Score:</span>{' '}
          <span className="font-medium">{matter.urgency_score}/100</span>
        </div>
        <div>
          <span className="text-gray-500">Created:</span>{' '}
          <span className="font-medium">{new Date(matter.created_at).toLocaleDateString()}</span>
        </div>
        {matter.intake_id && (
          <div>
            <span className="text-gray-500">From Intake:</span>{' '}
            <span className="font-medium">{matter.intake_id.slice(0, 8)}...</span>
          </div>
        )}
      </div>
      <div className="mt-6 p-3 bg-red-50 rounded text-xs text-red-700">
        All agent outputs and client communications for this matter require
        Human Approval Gate before delivery.
      </div>
    </div>
  );
}

function ApprovalsTab({ matterId }: { matterId: string }) {
  const [approvals, setApprovals] = useState<any[]>([]);

  useEffect(() => {
    api.getApprovals().then((all) => {
      setApprovals(all.filter((a: any) => a.matter_id === matterId));
    });
  }, [matterId]);

  return (
    <div className="space-y-3">
      <h3 className="font-semibold">Approvals for this matter</h3>
      {approvals.length === 0 ? (
        <p className="text-gray-500 text-sm">No approvals yet.</p>
      ) : (
        approvals.map((a: any) => (
          <div key={a.id} className={`p-4 rounded-lg border ${
            a.status === 'pending' ? 'bg-yellow-50 border-yellow-200' :
            a.status === 'approved' ? 'bg-green-50 border-green-200' :
            'bg-red-50 border-red-200'
          }`}>
            <div className="flex justify-between text-sm">
              <span>{a.object_type} ({a.object_id.slice(0, 8)}...)</span>
              <span className="font-medium uppercase">{a.status}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
