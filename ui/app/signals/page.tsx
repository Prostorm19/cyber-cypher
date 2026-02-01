'use client';

import { useState, useEffect } from 'react';
import { api, Signal } from '@/lib/api';
import { Card, Button, Alert, LoadingSpinner, Badge } from '@/components/ui';

export default function SignalsPage() {
    const [formData, setFormData] = useState({
        signal_type: 'support_ticket',
        merchant_id: '',
        migration_stage: 'mid_migration',
        category: '',
        severity: 'medium',
        title: '',
        description: '',
    });
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    // New state for displaying signals
    const [signals, setSignals] = useState<Signal[]>([]);
    const [loadingSignals, setLoadingSignals] = useState(true);
    const [signalsError, setSignalsError] = useState<string | null>(null);
    const [timeWindow, setTimeWindow] = useState(24);

    // Fetch signals on mount and when timeWindow changes
    useEffect(() => {
        fetchSignals();
    }, [timeWindow]);

    async function fetchSignals() {
        try {
            setLoadingSignals(true);
            setSignalsError(null);
            const response = await api.getSignals({ hours: timeWindow });
            setSignals(response.signals || []);
        } catch (err) {
            setSignalsError(err instanceof Error ? err.message : 'Failed to fetch signals');
        } finally {
            setLoadingSignals(false);
        }
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setLoading(true);
        setSuccess(false);
        setError(null);

        try {
            const signal: Signal = {
                id: `sig_${Date.now()}`,
                timestamp: new Date().toISOString(),
                signal_type: formData.signal_type,
                merchant_id: formData.merchant_id,
                migration_stage: formData.migration_stage,
                category: formData.category,
                severity: formData.severity,
                title: formData.title,
                description: formData.description,
            };

            await api.ingestSignals([signal]);
            setSuccess(true);

            // Reset form
            setFormData({
                ...formData,
                merchant_id: '',
                category: '',
                title: '',
                description: '',
            });
            
            // Refresh signals list
            await fetchSignals();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to ingest signal');
        } finally {
            setLoading(false);
        }
    }

    function getSeverityVariant(severity?: string): 'low' | 'medium' | 'high' | 'info' {
        if (severity === 'high' || severity === 'critical') return 'high';
        if (severity === 'medium') return 'medium';
        if (severity === 'low') return 'low';
        return 'info';
    }

    function formatTimestamp(timestamp: string): string {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else if (diffMins < 1440) {
            return `${Math.floor(diffMins / 60)}h ago`;
        } else {
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Signal Ingestion</h1>
                <p className="mt-2 text-gray-600">
                    <span className="font-semibold">OBSERVE Phase:</span> Submit new signals from support tickets, logs, or system events
                </p>
            </div>

            {success && (
                <Alert variant="success" title="Signal Ingested Successfully">
                    The signal has been added to the observation system and will be analyzed in the next agent cycle.
                </Alert>
            )}

            {error && (
                <Alert variant="error" title="Ingestion Failed">
                    {error}
                </Alert>
            )}

            {/* Recent Signals Display */}
            <Card 
                title={`Recent Signals (Last ${timeWindow}h)`}
                action={
                    <div className="flex items-center gap-3">
                        <select
                            value={timeWindow}
                            onChange={(e) => setTimeWindow(Number(e.target.value))}
                            className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            <option value={1}>1 hour</option>
                            <option value={6}>6 hours</option>
                            <option value={24}>24 hours</option>
                            <option value={72}>3 days</option>
                        </select>
                        <Button variant="secondary" size="sm" onClick={fetchSignals}>
                            Refresh
                        </Button>
                    </div>
                }
            >
                {loadingSignals ? (
                    <LoadingSpinner />
                ) : signalsError ? (
                    <Alert variant="error">
                        {signalsError}
                    </Alert>
                ) : signals.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                        <p className="text-lg mb-2">No signals ingested in the last {timeWindow} hours</p>
                        <p className="text-sm">Submit a signal below or load demo data from the <a href="/demo" className="text-blue-600 hover:underline">Demo page</a></p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="text-sm text-gray-600 mb-4">
                            Showing {signals.length} signal{signals.length !== 1 ? 's' : ''}
                        </div>
                        
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Merchant</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {signals.map((signal, idx) => (
                                        <tr key={signal.id || idx} className="hover:bg-gray-50">
                                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                                {formatTimestamp(signal.timestamp)}
                                            </td>
                                            <td className="px-4 py-3 whitespace-nowrap text-sm">
                                                <span className="text-gray-700 capitalize">
                                                    {signal.signal_type?.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 whitespace-nowrap text-sm font-mono text-gray-900">
                                                {signal.merchant_id || '-'}
                                            </td>
                                            <td className="px-4 py-3 whitespace-nowrap text-sm">
                                                <Badge variant={getSeverityVariant(signal.severity)}>
                                                    {signal.severity?.toUpperCase() || 'UNKNOWN'}
                                                </Badge>
                                            </td>
                                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 capitalize">
                                                {signal.category || '-'}
                                            </td>
                                            <td className="px-4 py-3 text-sm text-gray-700 max-w-md truncate" title={signal.description}>
                                                {signal.title || signal.description}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </Card>

            {/* Signal Submission Form */}
            <Card title="Submit New Signal">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Signal Type */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Signal Type *
                            </label>
                            <select
                                value={formData.signal_type}
                                onChange={(e) => setFormData({ ...formData, signal_type: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                            >
                                <option value="support_ticket">Support Ticket</option>
                                <option value="error_log">Error Log</option>
                                <option value="api_error">API Error</option>
                                <option value="webhook_failure">Webhook Failure</option>
                                <option value="checkout_issue">Checkout Issue</option>
                                <option value="migration_event">Migration Event</option>
                            </select>
                        </div>

                        {/* Migration Stage */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Migration Stage *
                            </label>
                            <select
                                value={formData.migration_stage}
                                onChange={(e) => setFormData({ ...formData, migration_stage: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                            >
                                <option value="pre_migration">Pre-Migration</option>
                                <option value="mid_migration">Mid-Migration</option>
                                <option value="post_migration">Post-Migration</option>
                                <option value="completed">Completed</option>
                            </select>
                        </div>

                        {/* Merchant ID */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Merchant ID *
                            </label>
                            <input
                                type="text"
                                value={formData.merchant_id}
                                onChange={(e) => setFormData({ ...formData, merchant_id: e.target.value })}
                                placeholder="merchant_123"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                            />
                        </div>

                        {/* Category */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Category *
                            </label>
                            <input
                                type="text"
                                value={formData.category}
                                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                placeholder="checkout, payment, general"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                            />
                        </div>

                        {/* Severity */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Severity
                            </label>
                            <select
                                value={formData.severity}
                                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                                <option value="critical">Critical</option>
                            </select>
                        </div>

                        {/* Title */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Title
                            </label>
                            <input
                                type="text"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                placeholder="Brief issue summary"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                    </div>

                    {/* Description */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Description *
                        </label>
                        <textarea
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Detailed description of the issue..."
                            rows={4}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            required
                        />
                    </div>

                    <div className="flex justify-end space-x-3">
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={() => setFormData({
                                signal_type: 'support_ticket',
                                merchant_id: '',
                                migration_stage: 'mid_migration',
                                category: '',
                                severity: 'medium',
                                title: '',
                                description: '',
                            })}
                        >
                            Reset
                        </Button>
                        <Button type="submit" variant="primary" loading={loading}>
                            Ingest Signal
                        </Button>
                    </div>
                </form>
            </Card>

            {/* Example Signals */}
            <Card title="Example Signals">
                <div className="space-y-3 text-sm">
                    <div className="p-3 bg-gray-50 rounded-lg">
                        <div className="font-medium text-gray-900">Checkout Authentication Issue</div>
                        <div className="text-gray-600 mt-1">
                            Type: checkout_issue | Stage: mid_migration | Severity: high
                        </div>
                        <div className="text-gray-500 mt-1">
                            "Customers report checkout page shows blank screen - auth token invalid"
                        </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                        <div className="font-medium text-gray-900">API Error Log</div>
                        <div className="text-gray-600 mt-1">
                            Type: error_log | Stage: mid_migration | Severity: medium
                        </div>
                        <div className="text-gray-500 mt-1">
                            "Auth token expired - checkout authentication failed"
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    );
}
