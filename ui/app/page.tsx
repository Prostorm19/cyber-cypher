'use client';

import { useState, useEffect } from 'react';
import { api, SignalStatistics } from '@/lib/api';
import { StatCard, Card, Badge, Alert, LoadingSpinner } from '@/components/ui';

export default function DashboardPage() {
  const [stats, setStats] = useState<SignalStatistics | null>(null);
  const [openIncidents, setOpenIncidents] = useState<number>(0);
  const [decisionCount, setDecisionCount] = useState<number>(0);
  const [systemStatus, setSystemStatus] = useState<'monitoring' | 'high-risk' | 'error'>('monitoring');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboard, 30000);
    return () => clearInterval(interval);
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError(null);

      // Load statistics
      const statsData = await api.getSignalStatistics(24);
      setStats(statsData);

      // Load open incidents
      const incidentsData = await api.getOpenIncidents();
      setOpenIncidents(incidentsData.count);

      // Load decisions
      const decisionsData = await api.getDecisions(10);
      setDecisionCount(decisionsData.count);

      // Check last decision for risk level
      if (decisionsData.decisions && decisionsData.decisions.length > 0) {
        const lastDecision = decisionsData.decisions[0];
        if (lastDecision.risk_level === 'high' && lastDecision.requires_human_approval) {
          setSystemStatus('high-risk');
        } else {
          setSystemStatus('monitoring');
        }
      }
    } catch (err) {
      console.error('Dashboard load error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      setSystemStatus('error');
    } finally {
      setLoading(false);
    }
  }

  if (loading && !stats) {
    return <LoadingSpinner size="lg" />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Supervisor Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Real-time monitoring of the AI agent's observe-reason-decide-act-explain loop
        </p>
      </div>

      {/* System Status Banner */}
      {systemStatus === 'high-risk' && (
        <Alert variant="error" title="High Risk - Human Approval Required">
          The agent has detected a high-risk situation. Review pending actions in the Actions tab.
        </Alert>
      )}

      {systemStatus === 'monitoring' && (
        <Alert variant="success" title="System Monitoring">
          Agent is actively monitoring signals. No critical issues detected.
        </Alert>
      )}

      {systemStatus === 'error' && error && (
        <Alert variant="error" title="Connection Error">
          {error}. Make sure the backend server is running at http://localhost:8000
        </Alert>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Signals Ingested (24h)"
          value={stats?.total_signals || 0}
          icon="📡"
        />
        <StatCard
          title="Unique Merchants"
          value={stats?.unique_merchants || 0}
          icon="👥"
        />
        <StatCard
          title="Open Incidents"
          value={openIncidents}
          icon="🚨"
        />
        <StatCard
          title="Agent Decisions"
          value={decisionCount}
          icon="🤖"
        />
      </div>

      {/* Signal Breakdown */}
      {stats && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="Signals by Type">
            <div className="space-y-3">
              {Object.entries(stats.by_type).length > 0 ? (
                Object.entries(stats.by_type).map(([type, count]) => (
                  <div key={type} className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {type.replace('_', ' ')}
                    </span>
                    <Badge variant="info">{count}</Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No signals detected</p>
              )}
            </div>
          </Card>

          <Card title="Merchants by Migration Stage">
            <div className="space-y-3">
              {Object.entries(stats.by_migration_stage).length > 0 ? (
                Object.entries(stats.by_migration_stage).map(([stage, count]) => (
                  <div key={stage} className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {stage.replace('_', ' ')}
                    </span>
                    <Badge variant="info">{count}</Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No migration data</p>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Agent Loop Visualization */}
      <Card title="Agent Loop Status">
        <div className="grid grid-cols-5 gap-4">
          {[
            { phase: 'OBSERVE', icon: '👁️', active: true },
            { phase: 'REASON', icon: '🧠', active: true },
            { phase: 'DECIDE', icon: '⚖️', active: true },
            { phase: 'ACT', icon: '⚡', active: systemStatus !== 'high-risk' },
            { phase: 'EXPLAIN', icon: '📖', active: true },
          ].map((step) => (
            <div
              key={step.phase}
              className={`text-center p-4 rounded-lg border-2 ${step.active
                ? 'border-green-500 bg-green-50'
                : 'border-yellow-500 bg-yellow-50'
                }`}
            >
              <div className="text-3xl mb-2">{step.icon}</div>
              <div className={`font-semibold text-sm ${step.active ? 'text-green-900' : 'text-yellow-900'}`}>{step.phase}</div>
              <div className={`text-xs mt-1 ${step.active ? 'text-green-700' : 'text-yellow-700'}`}>
                {step.active ? 'Active' : 'Pending Approval'}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Last Update */}
      {stats && (
        <div className="text-sm text-gray-500 text-center">
          Last updated: {new Date(stats.timestamp).toLocaleString()}
        </div>
      )}
    </div>
  );
}
