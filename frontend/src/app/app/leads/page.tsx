'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { track } from '@/lib/tracker';
import { useI18n } from '@/lib/i18n';
import ErrorCard from '@/components/ErrorCard';

interface Lead {
  id: string;
  tenant_id: string | null;
  source_type: string;
  vertical: string | null;
  status: string;
  contact_json: Record<string, any>;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-blue-100 text-blue-700',
  routed: 'bg-green-100 text-green-700',
  contacted: 'bg-yellow-100 text-yellow-700',
  converted: 'bg-purple-100 text-purple-700',
  lost: 'bg-gray-100 text-gray-500',
};

export default function LeadsPage() {
  const { t, locale } = useI18n();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [filter, setFilter] = useState('');

  const loadLeads = async () => {
    try {
      setError(false);
      const data = await api.getLeads();
      setLeads(data);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeads();
    track('page_view', { page: '/app/leads' });
  }, []);

  const filtered = filter ? leads.filter((l) => l.status === filter) : leads;
  const filterKeys = ['', 'new', 'routed', 'contacted', 'converted', 'lost'];

  if (loading) return <div className="p-8 text-gray-500">{t('common.loading')}</div>;
  if (error) return <div className="py-12"><ErrorCard onRetry={loadLeads} /></div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">{t('leads.title')}</h1>
      <p className="text-sm text-gray-500 mb-4">{t('leads.subtitle')}</p>

      <div className="flex flex-wrap gap-2 mb-4">
        {filterKeys.map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`text-xs px-3 py-1.5 rounded-full border transition ${
              filter === s ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'
            }`}
          >
            {s ? t(`leads.filters.${s}`) : t('leads.filters.all')} ({s === '' ? leads.length : leads.filter((l) => l.status === s).length})
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-12 text-gray-400">{t('leads.noLeads')}</div>
      ) : (
        <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3 font-medium">{t('leads.table.contact')}</th>
                <th className="text-left p-3 font-medium">{t('leads.table.vertical')}</th>
                <th className="text-left p-3 font-medium">{t('leads.table.source')}</th>
                <th className="text-left p-3 font-medium">{t('leads.table.status')}</th>
                <th className="text-left p-3 font-medium">{t('leads.table.date')}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((lead) => (
                <tr key={lead.id} className="border-b hover:bg-gray-50 transition">
                  <td className="p-3">
                    <div className="font-medium">{lead.contact_json?.name || lead.contact_json?.firm_name || 'N/A'}</div>
                    {lead.contact_json?.phone && <div className="text-xs text-gray-400">{lead.contact_json.phone}</div>}
                  </td>
                  <td className="p-3">
                    <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                      {lead.vertical ? t(`leads.verticals.${lead.vertical}`) : '-'}
                    </span>
                  </td>
                  <td className="p-3 text-gray-500">{lead.source_type}</td>
                  <td className="p-3">
                    <span className={`text-xs px-2 py-0.5 rounded ${STATUS_COLORS[lead.status] || 'bg-gray-100'}`}>
                      {t(`leads.filters.${lead.status}`) || lead.status}
                    </span>
                  </td>
                  <td className="p-3 text-xs text-gray-400">
                    {new Date(lead.created_at).toLocaleDateString(locale === 'es' ? 'es-MX' : 'en-US')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
