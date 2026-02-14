/**
 * Lightweight event tracker.
 * - Generates persistent anonymous_id (localStorage)
 * - Captures UTM params + referrer
 * - Fires events to POST /events/track
 * - Silent failure (never blocks UI)
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const ANON_KEY = 'legalops_anon_id';
const SESSION_KEY = 'legalops_session_id';

function generateId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}

export function getAnonymousId(): string {
  if (typeof window === 'undefined') return '';
  let id = localStorage.getItem(ANON_KEY);
  if (!id) {
    id = generateId();
    localStorage.setItem(ANON_KEY, id);
  }
  return id;
}

export function getSessionId(): string {
  if (typeof window === 'undefined') return '';
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id = generateId();
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export function getUTMParams(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  const params = new URLSearchParams(window.location.search);
  const utm: Record<string, string> = {};
  for (const key of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']) {
    const val = params.get(key);
    if (val) utm[key] = val;
  }
  return utm;
}

export async function track(
  name: string,
  properties: Record<string, any> = {},
): Promise<void> {
  if (typeof window === 'undefined') return;
  try {
    await fetch(`${API_URL}/events/track`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        anonymous_id: getAnonymousId(),
        session_id: getSessionId(),
        name,
        properties: {
          ...properties,
          ...getUTMParams(),
          referrer: document.referrer || '',
          path: window.location.pathname,
          url: window.location.href,
        },
      }),
    });
  } catch {
    // Silent failure – tracking should never block UI
  }
}

export async function trackPageView(extraProps: Record<string, any> = {}): Promise<void> {
  return track('page_view', extraProps);
}

/**
 * Assign a variant for an experiment. Returns the variant string.
 */
export async function getExperimentVariant(
  experimentKey: string,
): Promise<string> {
  if (typeof window === 'undefined') return 'control';
  try {
    const res = await fetch(`${API_URL}/experiments/assign`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        experiment_key: experimentKey,
        anonymous_id: getAnonymousId(),
      }),
    });
    if (!res.ok) return 'control';
    const data = await res.json();
    return data.variant || 'control';
  } catch {
    return 'control';
  }
}
