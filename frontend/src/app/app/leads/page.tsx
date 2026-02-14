'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { track } from '@/lib/tracker';

interface Lead {
  id: string;
  tenant_id: string | null;
  source_type: string;
  vertical: string | null;
  status: string;
  contact_json: Record<string, any>;
  created_at: string;
}

const VERTICAL_LABELS: Record<string, string> = {
  mx_divorce: 'Divorcio',
  mx_consumer: 'Consumidor',
  mx_labor: 'Laboral',
  immigration: 'Inmigración',
  tax_resolution: 'Fiscal',
};

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-blue-100 text-blue-700',
  routed: 'bg-green-100 text-green-700',
  contacted: 'bg-yellow-100 text-yellow-700',
  converted: 'bg-purple-100 text-purple-700',
  lost: 'bg-gray-100 text-gray-500',
};

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    loadLeads();
    track('page_view', { page: '/app/leads' });
  }, []);

  const loadLeads = async () => {
    try {
      const data = await api.getLeads();
      setLeads(data);
    } catch (err) {
      console.error('Leads load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = filter ? leads.filter((l) => l.status === filter) : leads;

  if (loading) {
    return <div className="p-8 text-gray-500">Cargando leads...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Leads</h1>
      <p className="text-sm text-gray-500 mb-4">
        Leads entrantes del canal B2C y B2B. Los leads se rutean automaticamente al despacho por vertical y region.
      </p>

      <div className="flex gap-2 mb-4">
        {['', 'new', 'routed', 'contacted', 'converted'].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`text-xs px-3 py-1.5 rounded-full border transition ${
              filter === s ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'
            }`}
          >
            {s || 'Todos'} {s === '' ? `(${leads.length})` : `(${leads.filter((l) => l.status === s).length})`}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-12 text-gray-400">Sin leads</div>
      ) : (
        <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3 font-medium">Nombre</th>
                <th className="text-left p-3 font-medium">Vertical</th>
                <th className="text-left p-3 font-medium">Canal</th>
                <th className="text-left p-3 font-medium">Contacto</th>
                <th className="text-left p-3 font-medium">Estado</th>
                <th className="text-left p-3 font-medium">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((lead) => (
                <tr key={lead.id} className="border-b hover:bg-gray-50 transition">
                  <td className="p-3 font-medium">
                    {lead.contact_json?.name || lead.contact_json?.firm_name || 'N/A'}
                  </td>
                  <td className="p-3">
                    <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                      {VERTICAL_LABELS[lead.vertical || ''] || lead.vertical || '-'}
                    </span>
                  </td>
                  <td className="p-3 text-gray-500">{lead.source_type}</td>
                  <td className="p-3 text-xs text-gray-500">
                    {lead.contact_json?.email && <div>{lead.contact_json.email}</div>}
                    {lead.contact_json?.phone && <div>{lead.contact_json.phone}</div>}
                  </td>
                  <td className="p-3">
                    <span className={`text-xs px-2 py-0.5 rounded ${STATUS_COLORS[lead.status] || 'bg-gray-100'}`}>
                      {lead.status}
                    </span>
                  </td>
                  <td className="p-3 text-xs text-gray-400">
                    {new Date(lead.created_at).toLocaleDateString('es-MX')}
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
