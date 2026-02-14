const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request(path: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

  // Intakes (public)
  createIntake: (data: any) =>
    request('/public/intake', { method: 'POST', body: JSON.stringify(data) }),
  getIntakes: () => request('/intakes/'),

  // Matters
  getMatters: () => request('/matters/'),
  getMatter: (id: string) => request(`/matters/${id}`),
  createMatter: (data: any) =>
    request('/matters/', { method: 'POST', body: JSON.stringify(data) }),

  // Documents
  getDocuments: (matterId: string) => request(`/documents/?matter_id=${matterId}`),
  uploadDocument: async (matterId: string, kind: string, file: File) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    const formData = new FormData();
    formData.append('matter_id', matterId);
    formData.append('kind', kind);
    formData.append('file', file);
    const res = await fetch(`${API_URL}/documents/upload`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
    return res.json();
  },

  // Tasks
  getTasks: (matterId?: string) =>
    request(`/tasks/${matterId ? `?matter_id=${matterId}` : ''}`),

  // Agent runs
  runAgent: (data: { matter_id: string; agent_name: string; input_data: any }) =>
    request('/agents/run', { method: 'POST', body: JSON.stringify(data) }),
  getAgentDefinitions: () => request('/agents/definitions'),

  // Approvals
  getApprovals: (status?: string) =>
    request(`/approvals/${status ? `?status=${status}` : ''}`),
  approveItem: (id: string, notes?: string) =>
    request(`/approvals/${id}/approve`, { method: 'POST', body: JSON.stringify({ notes }) }),
  rejectItem: (id: string, notes?: string) =>
    request(`/approvals/${id}/reject`, { method: 'POST', body: JSON.stringify({ notes }) }),

  // Messages
  createDraft: (data: { matter_id: string; channel: string; content: string }) =>
    request('/messages/draft', { method: 'POST', body: JSON.stringify(data) }),
  getDrafts: (matterId: string) => request(`/messages/?matter_id=${matterId}`),
  sendMessage: (draftId: string) =>
    request(`/messages/${draftId}/send`, { method: 'POST' }),

  // Interpreters
  createInterpreterRequest: (data: any) =>
    request('/interpreters/', { method: 'POST', body: JSON.stringify(data) }),
  getInterpreterRequests: (matterId?: string) =>
    request(`/interpreters/${matterId ? `?matter_id=${matterId}` : ''}`),

  // Analytics
  getAnalyticsOverview: (days: number = 7) =>
    request(`/app/analytics/overview?days=${days}`),
  getAnalyticsFunnel: (vertical: string = 'immigration', days: number = 30) =>
    request(`/app/analytics/funnel?vertical=${vertical}&days=${days}`),
  getPilotKPIs: (days: number = 7, slaHours: number = 4) =>
    request(`/app/analytics/pilot-kpis?days=${days}&sla_hours=${slaHours}`),

  // Pipeline
  getPipeline: () => request('/app/pipeline/'),
  changeIntakeStage: (intakeId: string, stage: string) =>
    request(`/app/pipeline/intake/${intakeId}/stage`, {
      method: 'PATCH', body: JSON.stringify({ stage }),
    }),
  changeMatterStage: (matterId: string, stage: string) =>
    request(`/app/pipeline/matter/${matterId}/stage`, {
      method: 'PATCH', body: JSON.stringify({ stage }),
    }),

  // Templates & Completeness
  getTemplate: (vertical: string) => request(`/templates/${vertical}`),
  getTemplates: () => request('/templates/'),
  getCompleteness: (matterId: string) => request(`/matters/${matterId}/completeness`),

  // Feedback
  submitFeedback: (data: { page: string; rating: number; text?: string; anonymous_id?: string; context?: any }) =>
    request('/feedback/', { method: 'POST', body: JSON.stringify(data) }),

  // Leads (authenticated)
  getLeads: (status?: string) =>
    request(`/app/leads${status ? `?status=${status}` : ''}`),
};
