'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import DocumentUploader from '@/components/DocumentUploader';
import TaskList from '@/components/TaskList';
import AgentRunPanel from '@/components/AgentRunPanel';
import MessageDraftEditor from '@/components/MessageDraftEditor';
import ErrorCard from '@/components/ErrorCard';

type Tab = 'overview' | 'documents' | 'tasks' | 'agents' | 'approvals' | 'messages';

export default function MatterDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { t } = useI18n();
  const [matter, setMatter] = useState<any>(null);
  const [tab, setTab] = useState<Tab>('overview');
  const [error, setError] = useState(false);

  useEffect(() => {
    api.getMatter(id).then(setMatter).catch(() => setError(true));
  }, [id]);

  if (error) return <div className="py-12"><ErrorCard onRetry={() => { setError(false); api.getMatter(id).then(setMatter).catch(() => setError(true)); }} /></div>;
  if (!matter) return <div className="p-4">{t('common.loading')}</div>;

  const tabs: { key: Tab; label: string }[] = [
    { key: 'overview', label: t('matter.tabs.overview') },
    { key: 'documents', label: t('matter.tabs.documents') },
    { key: 'tasks', label: t('matter.tabs.tasks') },
    { key: 'agents', label: t('matter.tabs.agents') },
    { key: 'approvals', label: t('matter.tabs.approvals') },
    { key: 'messages', label: t('matter.tabs.messages') },
  ];

  const urgencyColor =
    matter.urgency_score >= 70 ? 'text-red-600' :
    matter.urgency_score >= 40 ? 'text-yellow-600' : 'text-green-600';

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">
          {t(`leads.verticals.${matter.type}`) !== `leads.verticals.${matter.type}` ? t(`leads.verticals.${matter.type}`) : matter.type}
        </h1>
        <div className="flex flex-wrap gap-4 text-sm text-gray-600 mt-1">
          <span>ID: {matter.id.slice(0, 8)}...</span>
          <span>{t('matter.jurisdiction')}: {matter.jurisdiction}</span>
          <span className={urgencyColor}>{t('matter.urgency')}: {matter.urgency_score}/100</span>
          <span>{t('common.status')}: {matter.status}</span>
        </div>
      </div>

      <div className="flex border-b mb-6 overflow-x-auto">
        {tabs.map((tb) => (
          <button key={tb.key} onClick={() => setTab(tb.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition whitespace-nowrap ${
              tab === tb.key ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}>
            {tb.label}
          </button>
        ))}
      </div>

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
  const { t } = useI18n();
  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border">
      <h3 className="font-semibold mb-4">{t('matter.tabs.overview')}</h3>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div><span className="text-gray-500">{t('common.type')}:</span> <span className="font-medium">{matter.type}</span></div>
        <div><span className="text-gray-500">{t('matter.jurisdiction')}:</span> <span className="font-medium">{matter.jurisdiction}</span></div>
        <div><span className="text-gray-500">{t('common.status')}:</span> <span className="font-medium">{matter.status}</span></div>
        <div><span className="text-gray-500">{t('matter.urgency')}:</span> <span className="font-medium">{matter.urgency_score}/100</span></div>
      </div>
      <div className="mt-6 p-3 bg-red-50 rounded-lg text-xs text-red-700">{t('disclaimer.short')}</div>
    </div>
  );
}

function ApprovalsTab({ matterId }: { matterId: string }) {
  const { t } = useI18n();
  const [approvals, setApprovals] = useState<any[]>([]);

  useEffect(() => {
    api.getApprovals().then((all) => {
      setApprovals(all.filter((a: any) => a.matter_id === matterId));
    }).catch(() => {});
  }, [matterId]);

  return (
    <div className="space-y-3">
      <h3 className="font-semibold">{t('approvals.title')}</h3>
      {approvals.length === 0 ? (
        <p className="text-gray-500 text-sm">{t('approvals.noApprovals')}</p>
      ) : (
        approvals.map((a: any) => (
          <div key={a.id} className={`p-4 rounded-lg border ${
            a.status === 'pending' ? 'bg-yellow-50 border-yellow-200' :
            a.status === 'approved' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex justify-between text-sm">
              <span>{a.object_type} ({a.object_id?.slice(0, 8)}...)</span>
              <span className="font-medium uppercase">{a.status}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
