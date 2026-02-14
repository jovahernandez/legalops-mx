'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { track } from '@/lib/tracker';
import { useI18n } from '@/lib/i18n';
import ErrorCard from '@/components/ErrorCard';

const STAGE_KEYS = [
  'new_lead', 'intake_completed', 'docs_pending', 'expediente_draft',
  'pending_approval', 'approved', 'contract_onboarding', 'in_progress', 'closed',
];

const STAGE_COLORS: Record<string, string> = {
  new_lead: 'bg-gray-100',
  intake_completed: 'bg-blue-50',
  docs_pending: 'bg-yellow-50',
  expediente_draft: 'bg-orange-50',
  pending_approval: 'bg-indigo-50',
  approved: 'bg-green-50',
  contract_onboarding: 'bg-teal-50',
  in_progress: 'bg-purple-50',
  closed: 'bg-gray-50',
};

interface PipelineItem {
  id: string;
  entity_type: 'intake' | 'matter';
  pipeline_stage: string;
  type: string | null;
  client_name: string | null;
  urgency_score: number;
  created_at: string;
  intake_id: string | null;
  matter_id: string | null;
  days_in_stage: number;
  next_action: string | null;
}

export default function PipelinePage() {
  const { t } = useI18n();
  const [stages, setStages] = useState<Record<string, PipelineItem[]>>({});
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const loadPipeline = async () => {
    try {
      const data = await api.getPipeline();
      setStages(data.stages);
      setCounts(data.stage_counts);
      setError(false);
    } catch (err: any) {
      if (err.message?.includes('fetch')) setError(true);
      console.error('Pipeline load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPipeline();
    track('page_view', { page: '/app/pipeline' });
  }, []);

  const moveItem = async (item: PipelineItem, newStage: string) => {
    try {
      if (item.entity_type === 'intake') {
        await api.changeIntakeStage(item.id, newStage);
      } else {
        await api.changeMatterStage(item.id, newStage);
      }
      track('pipeline_stage_changed', {
        entity_type: item.entity_type,
        from_stage: item.pipeline_stage,
        to_stage: newStage,
      });
      loadPipeline();
    } catch (err) {
      console.error('Move error:', err);
    }
  };

  const stageIndex = (key: string) => STAGE_KEYS.indexOf(key);

  const verticalLabel = (type: string | null) => {
    if (!type) return 'general';
    const key = `leads.verticals.${type}`;
    const translated = t(key);
    return translated !== key ? translated : type;
  };

  if (error) return <div className="py-12"><ErrorCard onRetry={() => { setError(false); setLoading(true); loadPipeline(); }} /></div>;
  if (loading) return <div className="p-8 text-gray-500">{t('pipeline.loading')}</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">{t('pipeline.title')}</h1>
      <p className="text-sm text-gray-500 mb-6">{t('pipeline.subtitle')}</p>

      <div className="flex gap-3 overflow-x-auto pb-4">
        {STAGE_KEYS.map((key) => {
          const items = stages[key] || [];
          return (
            <div key={key} className={`flex-shrink-0 w-56 rounded-lg ${STAGE_COLORS[key] || 'bg-gray-50'} border`}>
              <div className="p-3 border-b font-semibold text-sm flex justify-between items-center">
                <span className="truncate">{t(`pipeline.stages.${key}`)}</span>
                <span className="bg-white text-gray-600 text-xs px-2 py-0.5 rounded-full">
                  {counts[key] || 0}
                </span>
              </div>
              <div className="p-2 space-y-2 min-h-[100px]">
                {items.map((item) => (
                  <div key={`${item.entity_type}-${item.id}`} className="bg-white rounded-lg p-3 shadow-sm border text-sm">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium truncate text-xs">
                        {item.client_name || t('pipeline.noName')}
                      </span>
                      {item.urgency_score > 50 && (
                        <span className="text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded ml-1">
                          {item.urgency_score}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 mb-1">
                      {verticalLabel(item.type)} &middot; {item.entity_type}
                    </div>
                    {item.days_in_stage > 0 && (
                      <div className={`text-xs ${item.days_in_stage > 3 ? 'text-red-500 font-medium' : 'text-gray-400'}`}>
                        {item.days_in_stage} {t('pipeline.daysInStage')}
                      </div>
                    )}
                    {item.next_action && (
                      <div className="text-xs text-blue-600 mt-1 italic truncate">{item.next_action}</div>
                    )}
                    <div className="flex gap-1 mt-2">
                      {stageIndex(key) > 0 && (
                        <button
                          onClick={() => moveItem(item, STAGE_KEYS[stageIndex(key) - 1])}
                          className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition"
                        >
                          &larr;
                        </button>
                      )}
                      {stageIndex(key) < STAGE_KEYS.length - 1 && (
                        <button
                          onClick={() => moveItem(item, STAGE_KEYS[stageIndex(key) + 1])}
                          className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded transition"
                        >
                          {t('pipeline.moveForward')} &rarr;
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                {items.length === 0 && (
                  <div className="text-xs text-gray-400 text-center py-4">{t('pipeline.noItems')}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
