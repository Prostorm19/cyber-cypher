'use client';

import { useState, useEffect } from 'react';
import { api, AgentDecision } from '@/lib/api';
import { Card, Badge, LoadingSpinner } from '@/components/ui';

export default function ExplainPage() {
    const [decision, setDecision] = useState<AgentDecision | null>(null);
    const [loading, setLoading] = useState(true);
    const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
        observations: true,
        hypothesis: true,
        reasoning: true,
        explainability: true,
    });

    useEffect(() => {
        loadLatestDecision();
    }, []);

    async function loadLatestDecision() {
        try {
            const decisionsData = await api.getDecisions(1);
            if (decisionsData.decisions && decisionsData.decisions.length > 0) {
                setDecision(decisionsData.decisions[0]);
            }
        } catch (err) {
            console.error('Failed to load decision:', err);
        } finally {
            setLoading(false);
        }
    }

    function toggleSection(section: string) {
        setExpandedSections({
            ...expandedSections,
            [section]: !expandedSections[section],
        });
    }

    const CollapsibleSection = ({
        title,
        icon,
        sectionKey,
        children
    }: {
        title: string;
        icon: string;
        sectionKey: string;
        children: React.ReactNode;
    }) => (
        <Card className="overflow-hidden">
            <button
                onClick={() => toggleSection(sectionKey)}
                className="w-full px-6 py-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
            >
                <div className="flex items-center space-x-3">
                    <span className="text-2xl">{icon}</span>
                    <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
                </div>
                <span className="text-2xl text-gray-400">
                    {expandedSections[sectionKey] ? '−' : '+'}
                </span>
            </button>
            {expandedSections[sectionKey] && (
                <div className="px-6 py-4 border-t border-gray-200">{children}</div>
            )}
        </Card>
    );

    if (loading) {
        return <LoadingSpinner size="lg" />;
    }

    if (!decision) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Explainability</h1>
                    <p className="mt-2 text-gray-600">No decisions available. Run an agent analysis first.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Explainability</h1>
                <p className="mt-2 text-gray-600">
                    <span className="font-semibold">EXPLAIN Phase:</span> Understand the AI's reasoning and decision-making process
                </p>
            </div>

            {/* Summary Card */}
            <Card title="Decision Summary">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <div className="text-sm text-gray-600">Decision Time</div>
                        <div className="mt-1 font-medium text-gray-900">
                            {new Date(decision.timestamp).toLocaleString()}
                        </div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-600">Confidence</div>
                        <div className="mt-1 font-bold text-2xl text-gray-900">
                            {(decision.hypothesis.confidence * 100).toFixed(0)}%
                        </div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-600">Risk Level</div>
                        <div className="mt-1">
                            <Badge variant={decision.risk_level as any}>
                                {decision.risk_level.toUpperCase()}
                            </Badge>
                        </div>
                    </div>
                </div>
            </Card>

            {/* Observations */}
            <CollapsibleSection title="Observations" icon="👁️" sectionKey="observations">
                <div className="space-y-2">
                    <p className="text-sm text-gray-600 mb-3">
                        What the agent observed in the system:
                    </p>
                    {decision.observations.map((obs, idx) => (
                        <div key={idx} className="flex items-start">
                            <span className="text-blue-600 mr-2 mt-0.5">▶</span>
                            <span className="text-gray-700">{obs}</span>
                        </div>
                    ))}
                </div>
            </CollapsibleSection>

            {/* Hypothesis */}
            <CollapsibleSection title="Hypothesis Formation" icon="💡" sectionKey="hypothesis">
                <div className="space-y-4">
                    <div>
                        <h4 className="font-semibold text-gray-900 mb-2">What the agent believes is happening:</h4>
                        <p className="text-gray-700 text-lg leading-relaxed">
                            {decision.hypothesis.description}
                        </p>
                    </div>

                    <div>
                        <h4 className="font-semibold text-gray-900 mb-2">
                            Why the agent is {(decision.hypothesis.confidence * 100).toFixed(0)}% confident:
                        </h4>
                        <ul className="space-y-2">
                            {decision.hypothesis.evidence.map((ev, idx) => (
                                <li key={idx} className="flex items-start">
                                    <span className="text-green-600 mr-2 mt-0.5">✓</span>
                                    <span className="text-gray-700">{ev}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Potential root causes identified:</h4>
                        <div className="flex flex-wrap gap-2">
                            {decision.hypothesis.potential_causes.map((cause, idx) => (
                                <Badge key={idx} variant="warning" className="text-sm">
                                    {cause}
                                </Badge>
                            ))}
                        </div>
                    </div>

                    {decision.hypothesis.uncertainty_notes && (
                        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <h4 className="font-semibold text-yellow-900 mb-1 flex items-center">
                                <span className="mr-2">⚠️</span>
                                What the agent is uncertain about:
                            </h4>
                            <p className="text-sm text-yellow-800">{decision.hypothesis.uncertainty_notes}</p>
                        </div>
                    )}
                </div>
            </CollapsibleSection>

            {/* Reasoning */}
            <CollapsibleSection title="Reasoning Process" icon="🧠" sectionKey="reasoning">
                <div className="space-y-3">
                    <p className="text-sm text-gray-600">
                        How the agent connected observations to conclusions:
                    </p>
                    <p className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">
                        {decision.reasoning}
                    </p>
                </div>
            </CollapsibleSection>

            {/* Explainability Notes */}
            <CollapsibleSection title="Decision Justification" icon="📖" sectionKey="explainability">
                <div className="space-y-4">
                    <div>
                        <h4 className="font-semibold text-gray-900 mb-2">
                            Why human approval was {decision.requires_human_approval ? 'REQUIRED' : 'NOT required'}:
                        </h4>
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <p className="text-gray-700 leading-relaxed">{decision.explainability_notes}</p>
                        </div>
                    </div>

                    {decision.requires_human_approval && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                            <h4 className="font-semibold text-red-900 mb-2 flex items-center">
                                <span className="mr-2">🛡️</span>
                                Safety Constraints in Effect:
                            </h4>
                            <ul className="text-sm text-red-800 space-y-1">
                                <li>• High-risk scenarios require explicit human approval</li>
                                <li>• Checkout/payment-related issues cannot be auto-resolved</li>
                                <li>• No automated modifications to live merchant systems</li>
                                <li>• All proposed actions are recommendations only</li>
                            </ul>
                        </div>
                    )}
                </div>
            </CollapsibleSection>

            {/* Transparency Statement */}
            <Card>
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
                    <h3 className="font-bold text-gray-900 mb-3 flex items-center">
                        <span className="mr-2 text-2xl">🔍</span>
                        Transparency Commitment
                    </h3>
                    <p className="text-gray-700 leading-relaxed">
                        This explainability view shows exactly what the AI agent observed, how it reasoned about
                        the data, what conclusions it reached, and why it made specific recommendations. The
                        system is designed to be fully transparent - no "black box" decisions. Every action
                        proposed by the agent includes confidence levels, evidence, and uncertainty notes so
                        human supervisors can make informed decisions about whether to approve them.
                    </p>
                </div>
            </Card>
        </div>
    );
}
