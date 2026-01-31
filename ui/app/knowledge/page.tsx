'use client';

import { useState } from 'react';
import { api, KnowledgeEntry } from '@/lib/api';
import { Card, Button, Badge, Alert } from '@/components/ui';

export default function KnowledgePage() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<KnowledgeEntry[]>([]);
    const [searching, setSearching] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [hasSearched, setHasSearched] = useState(false);

    async function handleSearch(e: React.FormEvent) {
        e.preventDefault();
        if (!query.trim()) return;

        setSearching(true);
        setError(null);
        setHasSearched(true);

        try {
            const data = await api.searchKnowledge(query);
            setResults(data.results || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Search failed');
        } finally {
            setSearching(false);
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
                <p className="mt-2 text-gray-600">
                    Search the system's long-term memory of resolved issues and learned patterns
                </p>
            </div>

            {/* Search */}
            <Card title="Search Knowledge Base">
                <form onSubmit={handleSearch} className="space-y-4">
                    <div>
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search for issues, solutions, patterns..."
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                        />
                    </div>
                    <div className="flex items-center space-x-3">
                        <Button type="submit" variant="primary" loading={searching}>
                            🔍 Search
                        </Button>
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={() => {
                                setQuery('');
                                setResults([]);
                                setHasSearched(false);
                            }}
                        >
                            Clear
                        </Button>
                    </div>
                    <div className="text-sm text-gray-500">
                        Try searching for: "checkout", "auth", "migration", "token"
                    </div>
                </form>
            </Card>

            {error && (
                <Alert variant="error" title="Search Error">
                    {error}
                </Alert>
            )}

            {/* Results */}
            {hasSearched && (
                <Card title={`Search Results (${results.length})`}>
                    {results.length > 0 ? (
                        <div className="space-y-4">
                            {results.map((entry) => (
                                <div key={entry.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                    <div className="flex items-start justify-between mb-3">
                                        <h3 className="text-lg font-semibold text-gray-900">{entry.title}</h3>
                                        <div className="flex items-center space-x-2">
                                            <Badge variant={entry.confidence >= 0.8 ? 'success' : 'warning'}>
                                                {(entry.confidence * 100).toFixed(0)}% confident
                                            </Badge>
                                            {entry.times_validated > 0 && (
                                                <Badge variant="info">
                                                    ✓ {entry.times_validated}x validated
                                                </Badge>
                                            )}
                                        </div>
                                    </div>

                                    <div className="space-y-3">
                                        <div>
                                            <h4 className="text-sm font-medium text-gray-700 mb-1">Issue Pattern:</h4>
                                            <p className="text-gray-600 text-sm">{entry.issue_pattern}</p>
                                        </div>

                                        <div>
                                            <h4 className="text-sm font-medium text-gray-700 mb-1">Root Cause:</h4>
                                            <p className="text-gray-600 text-sm">{entry.root_cause}</p>
                                        </div>

                                        <div>
                                            <h4 className="text-sm font-medium text-gray-700 mb-1">Resolution:</h4>
                                            <p className="text-gray-600 text-sm bg-green-50 border border-green-200 rounded p-2">
                                                {entry.resolution}
                                            </p>
                                        </div>

                                        {entry.tags && entry.tags.length > 0 && (
                                            <div className="flex flex-wrap gap-2 pt-2">
                                                {entry.tags.map((tag, idx) => (
                                                    <Badge key={idx} variant="info" className="text-xs">
                                                        {tag}
                                                    </Badge>
                                                ))}
                                            </div>
                                        )}

                                        <div className="text-xs text-gray-500 pt-2 border-t border-gray-200">
                                            Added: {new Date(entry.created_at).toLocaleDateString()}
                                            {entry.related_incidents.length > 0 && (
                                                <span className="ml-3">
                                                    Related incidents: {entry.related_incidents.length}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8">
                            <div className="text-gray-400 text-4xl mb-3">🔍</div>
                            <p className="text-gray-600">No results found for "{query}"</p>
                            <p className="text-gray-500 text-sm mt-2">
                                Try searching with different keywords
                            </p>
                        </div>
                    )}
                </Card>
            )}

            {/* Knowledge Base Info */}
            {!hasSearched && (
                <Card title="About the Knowledge Base">
                    <div className="space-y-4">
                        <p className="text-gray-700">
                            The knowledge base stores long-term memory of resolved incidents and validated
                            patterns. As the system encounters and resolves issues, it learns and builds a
                            repository of solutions.
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                <h4 className="font-semibold text-blue-900 mb-2">🧠 Learning System</h4>
                                <p className="text-sm text-blue-800">
                                    Each resolved incident can be converted into a knowledge entry, helping the
                                    system recognize and respond faster to similar issues in the future.
                                </p>
                            </div>
                            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                                <h4 className="font-semibold text-green-900 mb-2">✓ Validation Tracking</h4>
                                <p className="text-sm text-green-800">
                                    Knowledge entries gain confidence as they're validated through successful
                                    resolutions, improving the system's reliability over time.
                                </p>
                            </div>
                        </div>
                    </div>
                </Card>
            )}
        </div>
    );
}
