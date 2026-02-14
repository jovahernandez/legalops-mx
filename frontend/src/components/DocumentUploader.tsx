'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

const DOC_KINDS = [
  'id_document', 'tax_notice', 'court_notice', 'marriage_cert',
  'birth_cert', 'passport', 'pay_stub', 'bank_statement', 'other',
];

export default function DocumentUploader({ matterId }: { matterId: string }) {
  const [docs, setDocs] = useState<any[]>([]);
  const [kind, setKind] = useState('id_document');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDocs();
  }, [matterId]);

  const loadDocs = async () => {
    try {
      const data = await api.getDocuments(matterId);
      setDocs(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      await api.uploadDocument(matterId, kind, file);
      setFile(null);
      loadDocs();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <h3 className="font-semibold mb-4">Documents</h3>

      {/* Upload form */}
      <div className="bg-white p-4 rounded-lg shadow mb-4">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Document Type</label>
            <select
              className="w-full border rounded px-3 py-2 text-sm"
              value={kind}
              onChange={(e) => setKind(e.target.value)}
            >
              {DOC_KINDS.map((k) => (
                <option key={k} value={k}>{k.replace('_', ' ')}</option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">File</label>
            <input
              type="file"
              className="w-full text-sm"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="px-4 py-2 bg-blue-600 text-white rounded text-sm disabled:opacity-50"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
        {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
      </div>

      {/* Document list */}
      <div className="space-y-2">
        {docs.length === 0 ? (
          <p className="text-gray-500 text-sm">No documents uploaded yet.</p>
        ) : (
          docs.map((doc: any) => (
            <div key={doc.id} className="flex justify-between items-center bg-white p-3 rounded shadow-sm">
              <div>
                <p className="text-sm font-medium">{doc.filename}</p>
                <p className="text-xs text-gray-500">{doc.kind?.replace('_', ' ')}</p>
              </div>
              <span className={`text-xs px-2 py-1 rounded ${
                doc.status === 'uploaded' ? 'bg-blue-100 text-blue-700' :
                doc.status === 'verified' ? 'bg-green-100 text-green-700' :
                'bg-red-100 text-red-700'
              }`}>
                {doc.status}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
