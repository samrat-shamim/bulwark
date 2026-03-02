/**
 * Mock data for dashboard demo mode.
 * Shown to prospects who visit app.bulwark.live without an API key.
 */

import type { Agent, SessionSummary, Event, Stats } from '../types'
import type { AlertRule, AlertRecord } from '../api/client'

// Realistic timestamps: simulate an agent that's been running for ~12 minutes
const BASE = new Date()
function ago(ms: number): string {
  return new Date(BASE.getTime() - ms).toISOString()
}

export const DEMO_STATS: Stats = {
  active_sessions: 2,
  total_agents: 3,
  events_per_minute: 24,
  cost_24h: 1.87,
}

export const DEMO_AGENTS: { agents: Agent[] } = {
  agents: [
    { id: 'a1b2c3d4', name: 'customer-support-agent', active_sessions: 1, total_events_24h: 347, total_cost_24h: 1.24 },
    { id: 'e5f6a7b8', name: 'data-pipeline-agent', active_sessions: 1, total_events_24h: 128, total_cost_24h: 0.63 },
    { id: 'c9d0e1f2', name: 'code-review-agent', active_sessions: 0, total_events_24h: 42, total_cost_24h: 0.00 },
  ],
}

export const DEMO_SESSIONS: { sessions: SessionSummary[] } = {
  sessions: [
    {
      id: 'sess_f8a21b',
      agent_name: 'customer-support-agent',
      environment: 'production',
      started_at: ago(720_000),
      ended_at: null,
      killed_at: null,
      event_count: 34,
    },
    {
      id: 'sess_c3e09d',
      agent_name: 'data-pipeline-agent',
      environment: 'production',
      started_at: ago(540_000),
      ended_at: null,
      killed_at: null,
      event_count: 18,
    },
    {
      id: 'sess_a7b4e2',
      agent_name: 'customer-support-agent',
      environment: 'production',
      started_at: ago(3_600_000),
      ended_at: ago(2_400_000),
      killed_at: null,
      event_count: 67,
    },
    {
      id: 'sess_d1f5c8',
      agent_name: 'code-review-agent',
      environment: 'staging',
      started_at: ago(7_200_000),
      ended_at: null,
      killed_at: ago(6_900_000),
      event_count: 42,
    },
  ],
}

export const DEMO_EVENTS: { events: Event[] } = {
  events: ([
    {
      id: 'ev01', session_id: 'sess_f8a21b', event_type: 'session_start',
      timestamp: ago(720_000), duration_ms: null, status: 'success',
      payload: { sdk_version: '0.1.0', python_version: '3.12.1', framework: 'langchain' },
    },
    {
      id: 'ev02', session_id: 'sess_f8a21b', event_type: 'llm_call',
      timestamp: ago(718_000), duration_ms: 1240, status: 'success',
      payload: { model: 'claude-sonnet-4-6', input_tokens: 1200, output_tokens: 380, cost_usd: 0.0048 },
    },
    {
      id: 'ev03', session_id: 'sess_f8a21b', event_type: 'tool_call',
      timestamp: ago(716_000), duration_ms: 85, status: 'success',
      payload: { tool_name: 'search_kb', tool_input: { query: 'refund policy enterprise plan' } },
    },
    {
      id: 'ev04', session_id: 'sess_f8a21b', event_type: 'tool_call',
      timestamp: ago(714_000), duration_ms: 230, status: 'success',
      payload: { tool_name: 'lookup_customer', tool_input: { email: 'jane@acmecorp.com' } },
    },
    {
      id: 'ev05', session_id: 'sess_f8a21b', event_type: 'llm_call',
      timestamp: ago(712_000), duration_ms: 980, status: 'success',
      payload: { model: 'claude-sonnet-4-6', input_tokens: 2400, output_tokens: 520, cost_usd: 0.0089 },
    },
    {
      id: 'ev06', session_id: 'sess_f8a21b', event_type: 'action',
      timestamp: ago(710_000), duration_ms: 45, status: 'success',
      payload: { action: 'send_reply', target: 'jane@acmecorp.com' },
    },
    {
      id: 'ev07', session_id: 'sess_c3e09d', event_type: 'session_start',
      timestamp: ago(540_000), duration_ms: null, status: 'success',
      payload: { sdk_version: '0.1.0', python_version: '3.11.8', framework: 'manual' },
    },
    {
      id: 'ev08', session_id: 'sess_c3e09d', event_type: 'tool_call',
      timestamp: ago(538_000), duration_ms: 3200, status: 'success',
      payload: { tool_name: 'query_database', tool_input: { sql: 'SELECT count(*) FROM orders WHERE date > now() - interval \'24h\'' } },
    },
    {
      id: 'ev09', session_id: 'sess_c3e09d', event_type: 'llm_call',
      timestamp: ago(534_000), duration_ms: 2100, status: 'success',
      payload: { model: 'claude-sonnet-4-6', input_tokens: 4800, output_tokens: 1200, cost_usd: 0.021 },
    },
    {
      id: 'ev10', session_id: 'sess_c3e09d', event_type: 'tool_call',
      timestamp: ago(530_000), duration_ms: 150, status: 'success',
      payload: { tool_name: 'write_report', tool_input: { path: '/reports/daily-orders.md' } },
    },
    {
      id: 'ev11', session_id: 'sess_f8a21b', event_type: 'tool_call',
      timestamp: ago(600_000), duration_ms: 120, status: 'success',
      payload: { tool_name: 'search_kb', tool_input: { query: 'upgrade plan pricing tiers' } },
    },
    {
      id: 'ev12', session_id: 'sess_f8a21b', event_type: 'llm_call',
      timestamp: ago(595_000), duration_ms: 1500, status: 'success',
      payload: { model: 'claude-sonnet-4-6', input_tokens: 3100, output_tokens: 680, cost_usd: 0.012 },
    },
    {
      id: 'ev13', session_id: 'sess_f8a21b', event_type: 'tool_call',
      timestamp: ago(590_000), duration_ms: 340, status: 'failure',
      payload: { tool_name: 'send_slack_dm', tool_input: { channel: '#support-escalations', message: 'Customer requesting manual override' }, error: 'channel_not_found' },
    },
    {
      id: 'ev14', session_id: 'sess_d1f5c8', event_type: 'tool_call',
      timestamp: ago(6_950_000), duration_ms: 45000, status: 'killed',
      payload: { tool_name: 'run_tests', tool_input: { suite: 'integration', timeout: 300 } },
    },
    {
      id: 'ev15', session_id: 'sess_c3e09d', event_type: 'tool_call',
      timestamp: ago(480_000), duration_ms: 8900, status: 'success',
      payload: { tool_name: 'query_database', tool_input: { sql: 'SELECT product_id, sum(quantity) FROM order_items GROUP BY 1 ORDER BY 2 DESC LIMIT 20' } },
    },
    {
      id: 'ev16', session_id: 'sess_f8a21b', event_type: 'action',
      timestamp: ago(450_000), duration_ms: 60, status: 'success',
      payload: { action: 'create_ticket', target: 'SUPPORT-4821' },
    },
    {
      id: 'ev17', session_id: 'sess_f8a21b', event_type: 'llm_call',
      timestamp: ago(400_000), duration_ms: 890, status: 'success',
      payload: { model: 'claude-haiku-4-5', input_tokens: 600, output_tokens: 150, cost_usd: 0.0003 },
    },
    {
      id: 'ev18', session_id: 'sess_f8a21b', event_type: 'tool_call',
      timestamp: ago(350_000), duration_ms: 95, status: 'success',
      payload: { tool_name: 'search_kb', tool_input: { query: 'SLA response time commitments' } },
    },
    {
      id: 'ev19', session_id: 'sess_c3e09d', event_type: 'llm_call',
      timestamp: ago(300_000), duration_ms: 3400, status: 'success',
      payload: { model: 'claude-sonnet-4-6', input_tokens: 8200, output_tokens: 2100, cost_usd: 0.038 },
    },
    {
      id: 'ev20', session_id: 'sess_c3e09d', event_type: 'action',
      timestamp: ago(280_000), duration_ms: 200, status: 'success',
      payload: { action: 'send_email', target: 'ops-team@company.com' },
    },
  ] as Event[]).sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()),
}

export const DEMO_SESSION_DETAIL: { session: SessionSummary; events: Event[] } = {
  session: DEMO_SESSIONS.sessions[0],
  events: DEMO_EVENTS.events.filter(e => e.session_id === 'sess_f8a21b'),
}

export const DEMO_RULES: { rules: AlertRule[] } = {
  rules: [
    {
      id: 'rule01',
      name: 'Runaway Agent',
      description: 'Kill agents that make too many tool calls in a short window',
      enabled: true,
      condition: { metric: 'tool_call_count', operator: '>', threshold: 100, window_seconds: 300 },
      actions: [{ type: 'dashboard_notification' }, { type: 'auto_kill' }],
      cooldown_seconds: 300,
      created_at: ago(86_400_000),
      updated_at: ago(86_400_000),
    },
    {
      id: 'rule02',
      name: 'Cost Spike',
      description: 'Alert when LLM spend exceeds $5 in 24 hours',
      enabled: true,
      condition: { metric: 'llm_cost_usd', operator: '>', threshold: 5, window_seconds: 86400 },
      actions: [{ type: 'dashboard_notification' }, { type: 'webhook', url: 'https://hooks.slack.com/...' }],
      cooldown_seconds: 3600,
      created_at: ago(86_400_000),
      updated_at: ago(86_400_000),
    },
    {
      id: 'rule03',
      name: 'Long Session',
      description: 'Kill sessions running longer than 30 minutes',
      enabled: false,
      condition: { metric: 'session_duration', operator: '>', threshold: 1800, window_seconds: 1800 },
      actions: [{ type: 'auto_kill' }],
      cooldown_seconds: 600,
      created_at: ago(86_400_000),
      updated_at: ago(43_200_000),
    },
  ],
}

export const DEMO_ALERTS: { alerts: AlertRecord[] } = {
  alerts: [
    {
      id: 'alert01',
      rule_id: 'rule01',
      rule_name: 'Runaway Agent',
      session_id: 'sess_d1f5c8',
      metric_value: 142,
      threshold: 100,
      actions_taken: ['dashboard_notification', 'auto_kill'],
      acknowledged: true,
      created_at: ago(6_900_000),
    },
  ],
}

export const DEMO_UNREAD_ALERTS: { unread: number } = { unread: 1 }
