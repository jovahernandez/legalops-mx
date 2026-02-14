'use client';

import { useI18n } from '@/lib/i18n';

export default function MatterCard({ matter }: { matter: any }) {
  const { t } = useI18n();

  const urgencyColor =
    matter.urgency_score >= 70 ? 'border-red-400 bg-red-50' :
    matter.urgency_score >= 40 ? 'border-yellow-400 bg-yellow-50' :
    'border-green-400 bg-green-50';

  return (
    <div className={`border-l-4 rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition cursor-pointer ${urgencyColor}`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-sm">
          {t(`leads.verticals.${matter.type}`) !== `leads.verticals.${matter.type}` ? t(`leads.verticals.${matter.type}`) : matter.type}
        </h3>
        <span className={`text-xs px-2 py-1 rounded ${
          matter.status === 'open' ? 'bg-blue-100 text-blue-700' :
          matter.status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'
        }`}>{matter.status}</span>
      </div>
      <div className="text-sm text-gray-600 space-y-1">
        <p>{t('matter.jurisdiction')}: {matter.jurisdiction}</p>
        <p>{t('matter.urgency')}: {matter.urgency_score}/100</p>
        <p className="text-xs text-gray-400">{matter.id.slice(0, 8)}...</p>
      </div>
    </div>
  );
}
