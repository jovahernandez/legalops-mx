'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function TaskList({ matterId }: { matterId: string }) {
  const [tasks, setTasks] = useState<any[]>([]);

  useEffect(() => {
    api.getTasks(matterId).then(setTasks).catch(() => {});
  }, [matterId]);

  const statusIcon: Record<string, string> = {
    pending: '[ ]',
    in_progress: '[~]',
    completed: '[x]',
    cancelled: '[-]',
  };

  return (
    <div>
      <h3 className="font-semibold mb-4">Tasks</h3>
      {tasks.length === 0 ? (
        <p className="text-gray-500 text-sm">No tasks yet. Run an agent to generate tasks.</p>
      ) : (
        <div className="space-y-2">
          {tasks.map((task: any) => (
            <div key={task.id} className="flex items-start gap-3 bg-white p-3 rounded shadow-sm">
              <span className="font-mono text-sm text-gray-500 mt-0.5">
                {statusIcon[task.status] || '[ ]'}
              </span>
              <div className="flex-1">
                <p className="text-sm font-medium">{task.title}</p>
                {task.description && (
                  <p className="text-xs text-gray-500 mt-1">{task.description}</p>
                )}
                <div className="flex gap-3 mt-1 text-xs text-gray-400">
                  <span>Status: {task.status}</span>
                  {task.due_at && <span>Due: {new Date(task.due_at).toLocaleDateString()}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
