'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { track } from '@/lib/tracker';

const STAGES = [
  { key: 'new_lead', label: 'Nuevo Lead', color: 'bg-gray-100' },
  { key: 'intake_completed', label: 'Intake Completo', color: 'bg-blue-50' },
  { key: 'docs_pending', label: 'Docs Pendientes', color: 'bg-yellow-50' },
  { key: 'expediente_draft', label: 'Exp. Borrador', color: 'bg-orange-50' },
  { key: 'pending_approval', label: 'Por Aprobar', color: 'bg-indigo-50' },
  { key: 'approved', label: 'Aprobado', color: 'bg-green-50' },
  { key: 'contract_onboarding', label: 'Contrato', color: 'bg-teal-50' },
  { key: 'in_progress', label: 'En Proceso', color: 'bg-purple-50' },
  { key: 'closed', label: 'Cerrado', color: 'bg-gray-50' },
];

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
  const [stages, setStages] = useState<Record<string, PipelineItem[]>>({});
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  const loadPipeline = async () => {
    try {
      const data = await api.getPipeline();
      setStages(data.stages);
      setCounts(data.stage_counts);
    } catch (err) {
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

  const stageIndex = (key: string) => STAGES.findIndex((s) => s.key === key);

  const VERTICAL_LABELS: Record<string, string> = {
    mx_divorce: 'Divorcio',
    mx_consumer: 'Consumidor',
    mx_labor: 'Laboral',
    immigration: 'Inmigración',
    tax_resolution: 'Fiscal',
  };

  if (loading) {
    return <div className="p-8 text-gray-500">Cargando pipeline...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Pipeline</h1>
      <p className="text-sm text-gray-500 mb-6">
        Vista Kanban de todos los intakes y expedientes. Mueve elementos entre etapas.
      </p>

      <div className="flex gap-3 overflow-x-auto pb-4">
        {STAGES.map((stage) => {
          const items = stages[stage.key] || [];
          return (
            <div
              key={stage.key}
              className={`flex-shrink-0 w-56 rounded-lg ${stage.color} border`}
            >
              <div className="p-3 border-b font-semibold text-sm flex justify-between items-center">
                <span className="truncate">{stage.label}</span>
                <span className="bg-white text-gray-600 text-xs px-2 py-0.5 rounded-full">
                  {counts[stage.key] || 0}
                </span>
              </div>
              <div className="p-2 space-y-2 min-h-[100px]">
                {items.map((item) => (
                  <div
                    key={`${item.entity_type}-${item.id}`}
                    className="bg-white rounded-lg p-3 shadow-sm border text-sm"
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium truncate text-xs">
                        {item.client_name || 'Sin nombre'}
                      </span>
                      {item.urgency_score > 50 && (
                        <span className="text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded ml-1">
                          {item.urgency_score}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 mb-1">
                      {VERTICAL_LABELS[item.type || ''] || item.type || 'general'} &middot; {item.entity_type}
                    </div>
                    {item.days_in_stage > 0 && (
                      <div className={`text-xs ${item.days_in_stage > 3 ? 'text-red-500 font-medium' : 'text-gray-400'}`}>
                        {item.days_in_stage}d en etapa
                      </div>
                    )}
                    {item.next_action && (
                      <div className="text-xs text-blue-600 mt-1 italic truncate">
                        {item.next_action}
                      </div>
                    )}
                    <div className="flex gap-1 mt-2">
                      {stageIndex(stage.key) > 0 && (
                        <button
                          onClick={() => moveItem(item, STAGES[stageIndex(stage.key) - 1].key)}
                          className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition"
                        >
                          &larr;
                        </button>
                      )}
                      {stageIndex(stage.key) < STAGES.length - 1 && (
                        <button
                          onClick={() => moveItem(item, STAGES[stageIndex(stage.key) + 1].key)}
                          className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded transition"
                        >
                          Avanzar &rarr;
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                {items.length === 0 && (
                  <div className="text-xs text-gray-400 text-center py-4">
                    Sin elementos
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
