'use client';

import { useState } from 'react';
import { api, AgentDecision } from '@/lib/api';
import { Card, Button, Badge, ProgressBar, Alert, LoadingSpinner } from '@/components/ui';

export default function AgentPage() {
    const [decision, setDecision] = useState<AgentDecision | null>(null);
    const [timeWindow, setTimeWindow] = useState(24);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function runAnalysis() {
        setLoading(true);
        setError(null);

        try {
            const result = await api.runAnalysis({
                time_window_hours: timeWindow,
                auto_approve: false,
            });
            setDecision(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Analysis failed');
        } finally {
            setLoading(false);
        }
    }

    const getRiskBadge = (level: string) => {
        const variants: Record<string, 'low' | 'medium' | 'high'> = {
            low: 'low',
            medium: 'medium',
            high: 'high',
        };
        return <Badge variant={variants[level] || 'info'}>{level.toUpperCase()}</Badge>;
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Agent Analysis</h1>
                <p className="mt-2 text-gray-600">
                    <span className="font-semibold">REASON + DECIDE Phases:</span> Run pattern detection and hypothesis formulation
                </p>
            </div>

            {/* Analysis Controls */}
            <Card title="Run Analysis">
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Time Window (hours)
                        </label>
                        <input
                            type="number"
                            value={timeWindow}
                            onChange={(e) => setTimeWindow(parseInt(e.target.value) || 24)}
                            min="1"
                            max="168"
                            className="w-full md:w-48 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <p className="text-sm text-gray-500 mt-1">
                            Analyze signals from the past {timeWindow} hours
                        </p>
                    </div>

                    <div className="flex items-center space-x-3">
                        <Button onClick={runAnalysis} loading={loading} variant="primary">
                            🤖 Run Agent Analysis
                        </Button>
                        {decision && (
                            <span className="text-sm text-gray-600">
                                Last run: {new Date(decision.timestamp).toLocaleString()}
                            </span>
                        )}
                    </div>
                </div>
            </Card>

            {error && (
                <Alert variant="error" title="Analysis Error">
                    {error}
                </Alert>
            )}

            {loading && <LoadingSpinner size="lg" />}

            {/* Analysis Results */}
            {decision && !loading && (
                <div className="space-y-6">
                    {/* Observations */}
                    <Card title="🔍 Observations">
                        <div className="space-y-2">
                            {decision.observations.map((obs, idx) => (
                                <div key={idx} className="flex items-start">
                                    <span className="text-blue-600 mr-2">•</span>
                                    <span className="text-gray-700">{obs}</span>
                                </div>
                            ))}
                        </div>
                    </Card>

                    {/* Hypothesis */}
                    <Card title="💡 Hypothesis">
                        <div className="space-y-4">
                            <div>
                                <div className="text-lg font-semibold text-gray-900 mb-2">
                                    {decision.hypothesis.description}
                                </div>
                                <ProgressBar
                                    label="Confidence"
                                    value={decision.hypothesis.confidence * 100}
                                    variant={
                                        decision.hypothesis.confidence >= 0.75
                                            ? 'high'
                                            : decision.hypothesis.confidence >= 0.5
                                                ? 'medium'
                                                : 'low'
                                    }
                                />
                            </div>

                            <div>
                                <h4 className="font-medium text-gray-900 mb-2">Evidence:</h4>
                                <ul className="space-y-1">
                                    {decision.hypothesis.evidence.map((ev, idx) => (
                                        <li key={idx} className="text-sm text-gray-600 flex items-start">
                                            <span className="text-green-600 mr-2">✓</span>
                                            {ev}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {decision.hypothesis.potential_causes.length > 0 && (
                                <div>
                                    <h4 className="font-medium text-gray-900 mb-2">Potential Causes:</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {decision.hypothesis.potential_causes.map((cause, idx) => (
                                            <Badge key={idx} variant="warning">
                                                {cause}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {decision.hypothesis.uncertainty_notes && (
                                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                                    <h4 className="font-medium text-yellow-900 mb-1">Uncertainty Notes:</h4>
                                    <p className="text-sm text-yellow-800">{decision.hypothesis.uncertainty_notes}</p>
                                </div>
                            )}
                        </div>
                    </Card>

                    {/* Reasoning */}
                    <Card title="🧠 Reasoning">
                        <p className="text-gray-700 leading-relaxed">{decision.reasoning}</p>
                    </Card>

                    {/* Risk Assessment */}
                    <Card title="⚠️ Risk Assessment">
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-gray-700 font-medium">Risk Level:</span>
                                {getRiskBadge(decision.risk_level)}
                            </div>

                            <div className="flex items-center justify-between">
                                <span className="text-gray-700 font-medium">Human Approval Required:</span>
                                {decision.requires_human_approval ? (
                                    <Badge variant="error">✓ YES</Badge>
                                ) : (
                                    <Badge variant="success">✗ NO</Badge>
                                )}
                            </div>

                            {decision.risk_level === 'high' && (
                                <Alert variant="error" title="High Risk Detected">
                                    This scenario involves critical systems or multiple merchants. All actions require human approval before execution.
                                </Alert>
                            )}
                        </div>
                    </Card>

                    {/* Proposed Actions Preview */}
                    <Card title="⚡ Proposed Actions ({decision.proposed_actions.length})">
                        <div className="space-y-3">
                            {decision.proposed_actions.slice(0, 3).map((action, idx) => (
                                <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="font-medium text-gray-900">{action.action_type.replace('_', ' ').toUpperCase()}</div>
                                            <div className="text-sm text-gray-600 mt-1">{action.description}</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {decision.proposed_actions.length > 3 && (
                                <div className="text-sm text-gray-500 text-center">
                                    + {decision.proposed_actions.length - 3} more actions
                                </div>
                            )}
                            <div className="pt-3">
                                <Button
                                    onClick={() => window.location.href = '/actions'}
                                    variant="primary"
                                    className="w-full"
                                >
                                    Review & Approve Actions →
                                </Button>
                            </div>
                        </div>
                    </Card>
                </div>
            )}

            {!decision && !loading && (
                <div className="text-center py-12">
                    <div className="text-gray-400 text-5xl mb-4">🤖</div>
                    <p className="text-gray-600">Click "Run Agent Analysis" to start</p>
                </div>
            )}
        </div>
    );
}
