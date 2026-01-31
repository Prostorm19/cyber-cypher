'use client';

import { useState, useEffect } from 'react';
import { api, Incident } from '@/lib/api';
import { Card, Badge, LoadingSpinner, Alert } from '@/components/ui';

export default function IncidentsPage() {
    const [incidents, setIncidents] = useState<Incident[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadIncidents();
    }, []);

    async function loadIncidents() {
        try {
            setLoading(true);
            const data = await api.getOpenIncidents();
            setIncidents(data.incidents || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load incidents');
        } finally {
            setLoading(false);
        }
    }

    const getStatusBadge = (status: string) => {
        const variants: Record<string, 'success' | 'warning' | 'error' | 'info'> = {
            open: 'error',
            investigating: 'warning',
            resolved: 'success',
            closed: 'info',
        };
        return <Badge variant={variants[status] || 'info'}>{status.toUpperCase()}</Badge>;
    };

    if (loading) {
        return <LoadingSpinner size="lg" />;
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Incident Management</h1>
                <p className="mt-2 text-gray-600">
                    Track and manage open incidents detected by the supervisor system
                </p>
            </div>

            {error && (
                <Alert variant="error" title="Error Loading Incidents">
                    {error}
                </Alert>
            )}

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                    <div className="text-center">
                        <div className="text-4xl font-bold text-red-600">{incidents.length}</div>
                        <div className="text-sm text-gray-600 mt-1">Open Incidents</div>
                    </div>
                </Card>
                <Card>
                    <div className="text-center">
                        <div className="text-4xl font-bold text-yellow-600">
                            {incidents.filter((i) => i.status === 'investigating').length}
                        </div>
                        <div className="text-sm text-gray-600 mt-1">Under Investigation</div>
                    </div>
                </Card>
                <Card>
                    <div className="text-center">
                        <div className="text-4xl font-bold text-blue-600">
                            {incidents.reduce((acc, inc) => acc + (inc.signal_ids?.length || 0), 0)}
                        </div>
                        <div className="text-sm text-gray-600 mt-1">Total Signals</div>
                    </div>
                </Card>
            </div>

            {/* Incidents Table */}
            {incidents.length > 0 ? (
                <Card title="Active Incidents">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead>
                                <tr className="bg-gray-50">
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Incident ID
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Title
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Status
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Signals
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Created
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {incidents.map((incident) => (
                                    <tr key={incident.id} className="hover:bg-gray-50">
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            <div className="text-sm font-medium text-blue-600">{incident.id}</div>
                                        </td>
                                        <td className="px-4 py-4">
                                            <div className="text-sm font-medium text-gray-900">{incident.title}</div>
                                            <div className="text-sm text-gray-500 truncate max-w-md">
                                                {incident.description}
                                            </div>
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            {getStatusBadge(incident.status)}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            <Badge variant="info">{incident.signal_ids?.length || 0}</Badge>
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {new Date(incident.created_at).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </Card>
            ) : (
                <Card>
                    <div className="text-center py-12">
                        <div className="text-gray-400 text-5xl mb-4">✅</div>
                        <p className="text-gray-600 text-lg">No open incidents</p>
                        <p className="text-gray-500 text-sm mt-2">
                            The system is operating normally with no active issues.
                        </p>
                    </div>
                </Card>
            )}
        </div>
    );
}
