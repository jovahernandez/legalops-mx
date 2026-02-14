'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

const AGENTS = [
  { name: 'intake_specialist', label: 'Intake Specialist' },
  { name: 'tax_solutions_assistant', label: 'Tax Solutions Assistant' },
  { name: 'paralegal_ops_assistant', label: 'Paralegal Ops Assistant' },
  { name: 'client_personal_assistant', label: 'Client Personal Assistant' },
  { name: 'interpreter_coordinator', label: 'Interpreter Coordinator' },
  { name: 'mx_divorce_intake', label: 'MX Divorce Intake' },
];

export default function AgentRunPanel({ matterId }: { matterId: string }) {
  const [selectedAgent, setSelectedAgent] = useState(AGENTS[0].name);
  const [inputData, setInputData] = useState('{}');
  const [result, setResult] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');

  const handleRun = async () => {
    setRunning(true);
    setError('');
    setResult(null);
    try {
      let parsed = {};
      try {
        parsed = JSON.parse(inputData);
      } catch {
        setError('Invalid JSON in input data');
        setRunning(false);
        return;
      }
      const res = await api.runAgent({
        matter_id: matterId,
        agent_name: selectedAgent,
        input_data: parsed,
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <h3 className="font-semibold mb-4">Run Agent</h3>

      <div className="bg-white p-4 rounded-lg shadow mb-4">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Agent</label>
            <select
              className="w-full border rounded px-3 py-2 text-sm"
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
            >
              {AGENTS.map((a) => (
                <option key={a.name} value={a.name}>{a.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Input Data (JSON)</label>
          <textarea
            className="w-full border rounded px-3 py-2 text-sm font-mono"
            rows={4}
            value={inputData}
            onChange={(e) => setInputData(e.target.value)}
            placeholder='{"case_type": "immigration", "description": "..."}'
          />
        </div>

        <button
          onClick={handleRun}
          disabled={running}
          className="px-6 py-2 bg-purple-600 text-white rounded text-sm hover:bg-purple-700 disabled:opacity-50"
        >
          {running ? 'Running...' : 'Run Agent'}
        </button>
      </div>

      {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">{error}</div>}

      {result && (
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex justify-between items-center mb-3">
            <h4 className="font-semibold">Agent Output</h4>
            <span className={`text-xs px-2 py-1 rounded font-medium ${
              result.status === 'blocked' ? 'bg-red-100 text-red-700' :
              result.status === 'needs_approval' ? 'bg-yellow-100 text-yellow-700' :
              'bg-green-100 text-green-700'
            }`}>
              {result.status}
            </span>
          </div>

          {result.output_json?.compliance_flags?.length > 0 && (
            <div className="bg-red-50 border border-red-200 p-3 rounded mb-3">
              <p className="text-sm font-medium text-red-700">Policy Engine Flags:</p>
              <ul className="text-xs text-red-600 mt-1 list-disc list-inside">
                {result.output_json.compliance_flags.map((f: string, i: number) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}

          {result.output_json?.urgency_flags?.length > 0 && (
            <div className="bg-orange-50 border border-orange-200 p-3 rounded mb-3">
              <p className="text-sm font-medium text-orange-700">Urgency Flags:</p>
              <ul className="text-xs text-orange-600 mt-1 list-disc list-inside">
                {result.output_json.urgency_flags.map((f: string, i: number) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="mb-3">
            <p className="text-sm font-medium mb-1">Case Packet:</p>
            <pre className="text-xs bg-gray-50 p-3 rounded whitespace-pre-wrap">
              {result.output_json?.case_packet}
            </pre>
          </div>

          {result.output_json?.questions_to_ask?.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium mb-1">Questions to Ask:</p>
              <ul className="text-xs list-disc list-inside">
                {result.output_json.questions_to_ask.map((q: string, i: number) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="text-xs text-gray-500 mt-3 p-2 bg-gray-50 rounded">
            {result.output_json?.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
}
