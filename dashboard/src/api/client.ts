import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Agent, SessionSummary, Event, Stats } from '../types'
import {
  DEMO_AGENTS, DEMO_SESSIONS, DEMO_SESSION_DETAIL, DEMO_EVENTS,
  DEMO_STATS, DEMO_RULES, DEMO_ALERTS, DEMO_UNREAD_ALERTS,
} from '../demo/data'

const API_BASE = import.meta.env.VITE_API_URL || ''
const API_KEY = localStorage.getItem('bulwark_api_key') || ''

export function isDemoMode(): boolean {
  return !API_KEY
}

const headers = () => ({
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json',
})

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, { headers: headers() })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

// Agents
export function useAgents() {
  const demo = isDemoMode()
  return useQuery<{ agents: Agent[] }>({
    queryKey: ['agents'],
    queryFn: () => fetchJSON('/v1/agents'),
    enabled: !demo,
    refetchInterval: demo ? false : 3000,
    ...(demo ? { initialData: DEMO_AGENTS } : {}),
  })
}

// Sessions
export function useSessions() {
  const demo = isDemoMode()
  return useQuery<{ sessions: SessionSummary[] }>({
    queryKey: ['sessions'],
    queryFn: () => fetchJSON('/v1/sessions'),
    enabled: !demo,
    refetchInterval: demo ? false : 2000,
    ...(demo ? { initialData: DEMO_SESSIONS } : {}),
  })
}

// Session detail
export function useSession(sessionId: string | null) {
  const demo = isDemoMode()
  return useQuery<{ session: SessionSummary; events: Event[] }>({
    queryKey: ['session', sessionId],
    queryFn: () => fetchJSON(`/v1/sessions/${sessionId}`),
    enabled: !demo && !!sessionId,
    refetchInterval: demo ? false : 2000,
    ...(demo && sessionId ? {
      initialData: {
        session: DEMO_SESSIONS.sessions.find(s => s.id === sessionId) ?? DEMO_SESSION_DETAIL.session,
        events: DEMO_EVENTS.events.filter(e => e.session_id === sessionId),
      },
    } : {}),
  })
}

// Events feed
export function useEvents(since?: string) {
  const demo = isDemoMode()
  const params = new URLSearchParams({ limit: '100' })
  if (since) params.set('since', since)
  return useQuery<{ events: Event[] }>({
    queryKey: ['events', since],
    queryFn: () => fetchJSON(`/v1/events?${params}`),
    enabled: !demo,
    refetchInterval: demo ? false : 2000,
    ...(demo ? { initialData: DEMO_EVENTS } : {}),
  })
}

// Stats
export function useStats() {
  const demo = isDemoMode()
  return useQuery<Stats>({
    queryKey: ['stats'],
    queryFn: () => fetchJSON('/v1/stats'),
    enabled: !demo,
    refetchInterval: demo ? false : 3000,
    ...(demo ? { initialData: DEMO_STATS } : {}),
  })
}

// Kill session
export function useKillSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (sessionId: string) => {
      if (isDemoMode()) return { status: 'demo' }
      const res = await fetch(`${API_BASE}/v1/sessions/${sessionId}/kill`, {
        method: 'POST',
        headers: headers(),
      })
      if (!res.ok) throw new Error(`Kill failed: ${res.status}`)
      return res.json()
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sessions'] })
      qc.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}

// Alert Rules
export interface AlertRule {
  id: string
  name: string
  description: string
  enabled: boolean
  condition: { metric: string; operator: string; threshold: number; window_seconds: number }
  actions: { type: string; url?: string }[]
  cooldown_seconds: number
  created_at: string
  updated_at: string
}

export interface AlertRecord {
  id: string
  rule_id: string
  rule_name: string
  session_id: string
  metric_value: number
  threshold: number
  actions_taken: string[]
  acknowledged: boolean
  created_at: string
}

export function useAlertRules() {
  const demo = isDemoMode()
  return useQuery<{ rules: AlertRule[] }>({
    queryKey: ['rules'],
    queryFn: () => fetchJSON('/v1/rules'),
    enabled: !demo,
    refetchInterval: demo ? false : 5000,
    ...(demo ? { initialData: DEMO_RULES } : {}),
  })
}

export function useAlerts() {
  const demo = isDemoMode()
  return useQuery<{ alerts: AlertRecord[] }>({
    queryKey: ['alerts'],
    queryFn: () => fetchJSON('/v1/alerts'),
    enabled: !demo,
    refetchInterval: demo ? false : 3000,
    ...(demo ? { initialData: DEMO_ALERTS } : {}),
  })
}

export function useUnreadAlerts() {
  const demo = isDemoMode()
  return useQuery<{ unread: number }>({
    queryKey: ['alerts', 'unread'],
    queryFn: () => fetchJSON('/v1/alerts/unread'),
    enabled: !demo,
    refetchInterval: demo ? false : 3000,
    ...(demo ? { initialData: DEMO_UNREAD_ALERTS } : {}),
  })
}

export function useToggleRule() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (ruleId: string) => {
      if (isDemoMode()) return { status: 'demo' }
      const res = await fetch(`${API_BASE}/v1/rules/${ruleId}/toggle`, {
        method: 'POST',
        headers: headers(),
      })
      if (!res.ok) throw new Error(`Toggle failed: ${res.status}`)
      return res.json()
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['rules'] }),
  })
}

export function useAcknowledgeAlert() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (alertId: string) => {
      if (isDemoMode()) return { status: 'demo' }
      const res = await fetch(`${API_BASE}/v1/alerts/${alertId}/ack`, {
        method: 'POST',
        headers: headers(),
      })
      if (!res.ok) throw new Error(`Ack failed: ${res.status}`)
      return res.json()
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['alerts'] })
    },
  })
}

export function useCreateRule() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (rule: Omit<AlertRule, 'id' | 'created_at' | 'updated_at'>) => {
      if (isDemoMode()) return { status: 'demo' }
      const res = await fetch(`${API_BASE}/v1/rules`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(rule),
      })
      if (!res.ok) throw new Error(`Create failed: ${res.status}`)
      return res.json()
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['rules'] }),
  })
}

// API key management
export function setApiKey(key: string) {
  localStorage.setItem('bulwark_api_key', key)
  window.location.reload()
}

export function getApiKey(): string {
  return localStorage.getItem('bulwark_api_key') || ''
}
