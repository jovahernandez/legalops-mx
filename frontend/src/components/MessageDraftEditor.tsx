'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

const CHANNELS = ['email', 'sms', 'whatsapp', 'call_script'];

export default function MessageDraftEditor({ matterId }: { matterId: string }) {
  const [drafts, setDrafts] = useState<any[]>([]);
  const [channel, setChannel] = useState('email');
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDrafts();
  }, [matterId]);

  const loadDrafts = async () => {
    try {
      const data = await api.getDrafts(matterId);
      setDrafts(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCreate = async () => {
    if (!content.trim()) return;
    setSaving(true);
    setError('');
    try {
      await api.createDraft({ matter_id: matterId, channel, content });
      setContent('');
      loadDrafts();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSend = async (draftId: string) => {
    try {
      await api.sendMessage(draftId);
      loadDrafts();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const statusStyle: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700',
    needs_approval: 'bg-yellow-100 text-yellow-700',
    approved: 'bg-green-100 text-green-700',
    sent: 'bg-blue-100 text-blue-700',
  };

  return (
    <div>
      <h3 className="font-semibold mb-4">Message Drafts</h3>

      {/* Compose */}
      <div className="bg-white p-4 rounded-lg shadow mb-4">
        <p className="text-xs text-red-600 mb-3">
          All messages require Human Approval Gate before they can be sent.
        </p>
        <div className="flex gap-3 mb-3">
          <select
            className="border rounded px-3 py-2 text-sm"
            value={channel}
            onChange={(e) => setChannel(e.target.value)}
          >
            {CHANNELS.map((c) => (
              <option key={c} value={c}>{c.replace('_', ' ')}</option>
            ))}
          </select>
        </div>
        <textarea
          className="w-full border rounded px-3 py-2 text-sm mb-3"
          rows={4}
          placeholder="Type message content..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <button
          onClick={handleCreate}
          disabled={saving || !content.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded text-sm disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Create Draft (sends to approval)'}
        </button>
        {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
      </div>

      {/* Drafts list */}
      <div className="space-y-3">
        {drafts.map((d: any) => (
          <div key={d.id} className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs text-gray-500">{d.channel}</span>
              <span className={`text-xs px-2 py-1 rounded ${statusStyle[d.status] || ''}`}>
                {d.status}
              </span>
            </div>
            <p className="text-sm whitespace-pre-wrap">{d.content}</p>
            {d.status === 'approved' && (
              <button
                onClick={() => handleSend(d.id)}
                className="mt-3 px-4 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
              >
                Send (simulated)
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
