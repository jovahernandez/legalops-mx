export default function MatterCard({ matter }: { matter: any }) {
  const urgencyColor =
    matter.urgency_score >= 70 ? 'border-red-400 bg-red-50' :
    matter.urgency_score >= 40 ? 'border-yellow-400 bg-yellow-50' :
    'border-green-400 bg-green-50';

  const typeLabel: Record<string, string> = {
    immigration: 'Immigration',
    tax_resolution: 'Tax Resolution',
    mx_divorce: 'Divorcio MX',
    interpreter: 'Interpreter',
    other: 'Other',
  };

  return (
    <div className={`border-l-4 rounded-lg p-4 bg-white shadow hover:shadow-md transition cursor-pointer ${urgencyColor}`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold">{typeLabel[matter.type] || matter.type}</h3>
        <span className={`text-xs px-2 py-1 rounded ${
          matter.status === 'open' ? 'bg-blue-100 text-blue-700' :
          matter.status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {matter.status}
        </span>
      </div>
      <div className="text-sm text-gray-600 space-y-1">
        <p>Jurisdiction: {matter.jurisdiction}</p>
        <p>Urgency: {matter.urgency_score}/100</p>
        <p className="text-xs text-gray-400">{matter.id.slice(0, 8)}...</p>
      </div>
    </div>
  );
}
