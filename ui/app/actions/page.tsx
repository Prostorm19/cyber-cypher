'use client';

import { useState, useEffect } from 'react';
import { api, AgentDecision, ProposedAction } from '@/lib/api';
import { Card, Button, Badge, Alert, LoadingSpinner } from '@/components/ui';

export default function ActionsPage() {
    const [decision, setDecision] = useState<AgentDecision | null>(null);
    const [selectedActions, setSelectedActions] = useState<number[]>([]);
    const [loading, setLoading] = useState(true);
    const [executing, setExecuting] = useState(false);
    const [results, setResults] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadLatestDecision();
    }, []);

    async function loadLatestDecision() {
        try {
            setLoading(true);
            const decisionsData = await api.getDecisions(1);
            if (decisionsData.decisions && decisionsData.decisions.length > 0) {
                setDecision(decisionsData.decisions[0]);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load decisions');
        } finally {
            setLoading(false);
        }
    }

    async function approveSelectedActions() {
        if (selectedActions.length === 0) {
            alert('Please select at least one action to approve');
            return;
        }

        setExecuting(true);
        setError(null);

        try {
            const result = await api.approveActions(selectedActions);
            setResults(result);
            setSelectedActions([]);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to execute actions');
        } finally {
            setExecuting(false);
        }
    }

    function toggleAction(index: number) {
        if (selectedActions.includes(index)) {
            setSelectedActions(selectedActions.filter((i) => i !== index));
        } else {
            setSelectedActions([...selectedActions, index]);
        }
    }

    const getActionIcon = (type: string) => {
        const icons: Record<string, string> = {
            draft_support_response: '📝',
            escalate_to_engineering: '🚀',
            alert_support_team: '📢',
            suggest_documentation: '📚',
            monitor_pattern: '👁️',
            create_incident_summary: '📋',
        };
        return icons[type] || '⚡';
    };

    if (loading) {
        return <LoadingSpinner size="lg" />;
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Action Approval</h1>
                <p className="mt-2 text-gray-600">
                    <span className="font-semibold">ACT Phase:</span> Review and approve agent-proposed actions with human-in-the-loop control
                </p>
            </div>

            {!decision && (
                <Alert variant="info" title="No Actions Available">
                    Run an agent analysis first to see proposed actions.{' '}
                    <a href="/agent" className="font-semibold underline">
                        Go to Agent Analysis
                    </a>
                </Alert>
            )}

            {decision && (
                <>
                    {/* Safety Banner */}
                    <Alert
                        variant={decision.requires_human_approval ? 'error' : 'warning'}
                        title={decision.requires_human_approval ? '🛡️ Human Approval Required' : 'Safety Controls Active'}
                    >
                        {decision.requires_human_approval ? (
                            <>
                                This decision involves <strong>{decision.risk_level.toUpperCase()} RISK</strong> scenarios.
                                All actions must be explicitly approved before execution. The system will NOT act autonomously.
                            </>
                        ) : (
                            'Low-risk actions may auto-execute, but you can review them here before approving.'
                        )}
                    </Alert>

                    {/* Risk Summary */}
                    <Card title="Risk Summary">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <div className="text-sm text-gray-600">Risk Level</div>
                                <div className="mt-1">
                                    <Badge variant={decision.risk_level as any}>
                                        {decision.risk_level.toUpperCase()}
                                    </Badge>
                                </div>
                            </div>
                            <div>
                                <div className="text-sm text-gray-600">Proposed Actions</div>
                                <div className="mt-1 text-2xl font-bold text-gray-900">
                                    {decision.proposed_actions.length}
                                </div>
                            </div>
                            <div>
                                <div className="text-sm text-gray-600">Approval Status</div>
                                <div className="mt-1">
                                    {results ? (
                                        <Badge variant="success">✓ {results.approved_count} Executed</Badge>
                                    ) : (
                                        <Badge variant="warning">Pending Review</Badge>
                                    )}
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Actions List */}
                    <Card title="Proposed Actions">
                        <div className="space-y-4">
                            {decision.proposed_actions.map((action, idx) => (
                                <div
                                    key={idx}
                                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${selectedActions.includes(idx)
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:border-gray-300'
                                        }`}
                                    onClick={() => toggleAction(idx)}
                                >
                                    <div className="flex items-start">
                                        <input
                                            type="checkbox"
                                            checked={selectedActions.includes(idx)}
                                            onChange={() => toggleAction(idx)}
                                            className="mt-1 mr-3 h-5 w-5"
                                            onClick={(e) => e.stopPropagation()}
                                        />
                                        <div className="flex-1">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-2">
                                                    <span className="text-2xl">{getActionIcon(action.action_type)}</span>
                                                    <h4 className="font-semibold text-gray-900">
                                                        {action.action_type.replace(/_/g, ' ').toUpperCase()}
                                                    </h4>
                                                </div>
                                                <Badge variant="info">Action #{idx + 1}</Badge>
                                            </div>
                                            <p className="text-gray-700 mt-2">{action.description}</p>
                                            {action.target && (
                                                <div className="mt-2 text-sm text-gray-600">
                                                    <strong>Target:</strong> {action.target}
                                                </div>
                                            )}
                                            <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-sm text-green-800">
                                                <strong>Expected Impact:</strong> {action.expected_impact}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-6 flex items-center justify-between">
                            <div className="text-sm text-gray-600">
                                {selectedActions.length} of {decision.proposed_actions.length} actions selected
                            </div>
                            <div className="flex space-x-3">
                                <Button
                                    variant="secondary"
                                    onClick={() => setSelectedActions([])}
                                    disabled={selectedActions.length === 0}
                                >
                                    Deselect All
                                </Button>
                                <Button
                                    variant="success"
                                    onClick={approveSelectedActions}
                                    loading={executing}
                                    disabled={selectedActions.length === 0}
                                >
                                    ✓ Approve Selected Actions
                                </Button>
                            </div>
                        </div>
                    </Card>

                    {/* Execution Results */}
                    {results && (
                        <Card title="✅ Execution Results">
                            <Alert variant="success" title="Actions Executed Successfully">
                                {results.approved_count} action(s) have been executed.
                            </Alert>
                            {results.results && (
                                <div className="mt-4 space-y-3">
                                    {results.results.map((result: any, idx: number) => (
                                        <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                                            <div className="flex items-center justify-between">
                                                <span className="font-medium text-gray-900">
                                                    {result.action_type?.replace(/_/g, ' ').toUpperCase()}
                                                </span>
                                                <Badge variant="success">{result.status}</Badge>
                                            </div>
                                            <p className="text-sm text-gray-600 mt-1">{result.message}</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </Card>
                    )}

                    {error && (
                        <Alert variant="error" title="Execution Error">
                            {error}
                        </Alert>
                    )}
                </>
            )}
        </div>
    );
}
