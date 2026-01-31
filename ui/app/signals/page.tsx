'use client';

import { useState } from 'react';
import { api, Signal } from '@/lib/api';
import { Card, Button, Alert } from '@/components/ui';

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
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to ingest signal');
        } finally {
            setLoading(false);
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
