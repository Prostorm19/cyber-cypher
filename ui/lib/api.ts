/**
 * API Client for Self-Healing Support Supervisor
 * TypeScript types and client methods for backend communication
 */

// ============================================================================
// TypeScript Types (matching backend Pydantic models)
// ============================================================================

export type SignalType =
  | 'support_ticket'
  | 'error_log'
  | 'migration_event'
  | 'webhook_failure'
  | 'api_error'
  | 'checkout_issue';

export type MigrationStage =
  | 'pre_migration'
  | 'mid_migration'
  | 'post_migration'
  | 'completed';

export type RiskLevel = 'low' | 'medium' | 'high';

export type ActionType =
  | 'draft_support_response'
  | 'escalate_to_engineering'
  | 'alert_support_team'
  | 'suggest_documentation'
  | 'monitor_pattern'
  | 'create_incident_summary';

export interface Signal {
  id: string;
  timestamp: string;
  signal_type: SignalType | string;
  merchant_id?: string;
  migration_stage?: MigrationStage | string;
  title?: string;
  description: string;
  metadata?: Record<string, unknown>;
  severity?: string;
  category?: string;
}

export interface Pattern {
  id: string;
  pattern_type: string;
  affected_merchants: string[];
  signal_ids: string[];
  first_seen: string;
  last_seen: string;
  frequency: number;
  description: string;
  common_attributes?: Record<string, unknown>;
}

export interface Hypothesis {
  description: string;
  confidence: number;
  evidence: string[];
  affected_patterns?: string[];
  potential_causes?: string[];
  uncertainty_notes?: string;
}

export interface ProposedAction {
  action_type: ActionType;
  description: string;
  target?: string;
  parameters?: Record<string, unknown>;
  expected_impact: string;
}

export interface AgentDecision {
  observations: string[];
  hypothesis: Hypothesis;
  reasoning: string;
  proposed_actions: ProposedAction[];
  risk_level: RiskLevel;
  requires_human_approval: boolean;
  explainability_notes: string;
  timestamp: string;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  pattern_ids?: string[];
  signal_ids?: string[];
  decisions?: AgentDecision[];
  resolution?: string;
  resolved_at?: string;
}

export interface KnowledgeEntry {
  id: string;
  title: string;
  issue_pattern: string;
  root_cause: string;
  resolution: string;
  created_at: string;
  tags?: string[];
  related_incidents?: string[];
  confidence: number;
  times_validated: number;
}

export interface SignalStatistics {
  total_signals: number;
  unique_merchants: number;
  by_type: Record<string, number>;
  by_migration_stage: Record<string, number>;
  timestamp: string;
}

export interface ActionResult {
  action_id: string;
  status: 'success' | 'failed' | 'pending';
  message: string;
  executed_at: string;
}

// ============================================================================
// API Client Configuration
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log(`[API Client] Fetching: ${url}`);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new APIError(
        error.detail || `API request failed: ${response.statusText}`,
        response.status,
        error
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : 'Network error',
      undefined,
      error
    );
  }
}

// ============================================================================
// API Client Methods
// ============================================================================

export const api = {
  // -------------------------
  // Signals
  // -------------------------

  /**
   * Ingest new signals into the system
   */
  async ingestSignals(signals: Signal[]): Promise<{ message: string; count: number }> {
    return fetchAPI('/signals/ingest', {
      method: 'POST',
      body: JSON.stringify({ signals }),
    });
  },

  /**
   * Get signal statistics for a time window
   */
  async getSignalStatistics(hours: number = 24): Promise<SignalStatistics> {
    return fetchAPI(`/signals/statistics?hours=${hours}`);
  },

  /**
   * Get recent signals
   */
  async getSignals(params?: {
    hours?: number;
    signal_type?: string;
    merchant_id?: string;
  }): Promise<{ count: number; signals: Signal[] }> {
    const query = new URLSearchParams();
    if (params?.hours) query.set('hours', params.hours.toString());
    if (params?.signal_type) query.set('signal_type', params.signal_type);
    if (params?.merchant_id) query.set('merchant_id', params.merchant_id);

    const endpoint = `/signals/recent${query.toString() ? `?${query.toString()}` : ''}`;
    return fetchAPI(endpoint);
  },

  // -------------------------
  // Agent
  // -------------------------

  /**
   * Run the agent analysis cycle
   */
  async runAnalysis(params: {
    time_window_hours?: number;
    auto_approve?: boolean;
  }): Promise<AgentDecision> {
    return fetchAPI('/agent/analyze', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  /**
   * Get agent decisions
   */
  async getDecisions(limit: number = 10): Promise<{
    decisions: AgentDecision[];
    count: number;
  }> {
    return fetchAPI(`/agent/decisions?limit=${limit}`);
  },

  /**
   * Get latest agent decision
   */
  async getLatestDecision(): Promise<AgentDecision | null> {
    const result = await this.getDecisions(1);
    return result.decisions.length > 0 ? result.decisions[0] : null;
  },

  // -------------------------
  // Actions
  // -------------------------

  /**
   * Execute an action with approval
   */
  async executeAction(params: {
    action: ProposedAction;
    approved: boolean;
  }): Promise<ActionResult> {
    return fetchAPI('/actions/execute', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  /**
   * Approve multiple actions by index from last decision
   */
  async approveActions(actionIndices: number[]): Promise<{
    status: string;
    approved_count: number;
    results: ActionResult[];
  }> {
    return fetchAPI('/agent/approve-actions', {
      method: 'POST',
      body: JSON.stringify({ action_indices: actionIndices }),
    });
  },

  // -------------------------
  // Incidents
  // -------------------------

  /**
   * Get open incidents
   */
  async getOpenIncidents(): Promise<{ count: number; incidents: Incident[] }> {
    return fetchAPI('/incidents/open');
  },

  /**
   * Get single incident by ID (Note: This endpoint may not exist in backend yet)
   */
  async getIncident(id: string): Promise<Incident> {
    return fetchAPI(`/incidents/${id}`);
  },

  /**
   * Update incident status (Note: This endpoint may not exist in backend yet)
   */
  async updateIncidentStatus(
    id: string,
    status: Incident['status'],
    resolution?: string
  ): Promise<Incident> {
    return fetchAPI(`/incidents/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status, resolution }),
    });
  },

  // -------------------------
  // Knowledge Base
  // -------------------------

  /**
   * Search knowledge base
   */
  async searchKnowledge(query: string, tags?: string[]): Promise<{
    results: KnowledgeEntry[];
    count: number;
  }> {
    const params = new URLSearchParams({ q: query });
    if (tags && tags.length > 0) {
      params.set('tags', tags.join(','));
    }
    return fetchAPI(`/knowledge/search?${params.toString()}`);
  },

  /**
   * Get all knowledge entries (Note: This endpoint may not exist in backend yet)
   */
  async getKnowledgeEntries(limit: number = 50): Promise<{
    entries: KnowledgeEntry[];
  }> {
    return fetchAPI(`/knowledge?limit=${limit}`);
  },

  /**
   * Get knowledge entry by ID
   */
  async getKnowledgeEntry(id: string): Promise<KnowledgeEntry> {
    return fetchAPI(`/knowledge/${id}`);
  },

  /**
   * Create knowledge entry
   */
  async createKnowledgeEntry(entry: Omit<KnowledgeEntry, 'id' | 'created_at' | 'times_validated'>): Promise<KnowledgeEntry> {
    return fetchAPI('/knowledge', {
      method: 'POST',
      body: JSON.stringify(entry),
    });
  },

  // -------------------------
  // Health Check
  // -------------------------

  /**
   * Check API health
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return fetchAPI('/health');
  },
};

// ============================================================================
// Export Types and Client
// ============================================================================

export { APIError };
export default api;
