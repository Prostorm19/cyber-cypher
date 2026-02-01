'use client';

import { useState } from 'react';
import { Card, Button, LoadingSpinner, Alert } from '@/components/ui';

interface Scenario {
  id: string;
  name: string;
  description: string;
  signal_count: number;
  severity: string;
  demonstrates: string[];
}

export default function DemoPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loadedScenarios, setLoadedScenarios] = useState(false);

  // Load available scenarios on mount
  useState(() => {
    if (!loadedScenarios) {
      fetch('http://localhost:8000/api/demo-scenarios')
        .then(res => res.json())
        .then(data => {
          setScenarios(data.scenarios || []);
          setLoadedScenarios(true);
        })
        .catch(err => console.error('Failed to load scenarios:', err));
    }
  });

  const loadDemoData = async (scenario: string) => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/load-demo-data?scenario=${scenario}`,
        { method: 'POST' }
      );

      const data = await response.json();
      setResult(data);
    } catch (error: any) {
      setResult({
        status: 'error',
        message: error.message || 'Failed to load demo data'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Demo Data Loader</h1>
          <p className="text-gray-600">
            Quickly load realistic scenarios to demonstrate the system's capabilities
          </p>
        </div>

        {/* Scenarios */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {scenarios.map((scenario) => (
            <Card key={scenario.id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-lg">{scenario.name}</h3>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${
                      scenario.severity === 'high'
                        ? 'bg-red-100 text-red-800'
                        : scenario.severity === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {scenario.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{scenario.description}</p>
                <p className="text-xs text-gray-500 mb-3">
                  📊 {scenario.signal_count} signals
                </p>
                
                <div className="mb-4">
                  <p className="text-xs font-medium text-gray-700 mb-1">Demonstrates:</p>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {scenario.demonstrates.map((item, idx) => (
                      <li key={idx}>• {item}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <Button
                onClick={() => loadDemoData(scenario.id)}
                disabled={loading}
                className="w-full"
              >
                {loading ? 'Loading...' : 'Load This Scenario'}
              </Button>
            </Card>
          ))}
        </div>

        {/* Loading State */}
        {loading && (
          <Card className="p-8 text-center">
            <LoadingSpinner />
            <p className="mt-4 text-gray-600">Loading demo data...</p>
          </Card>
        )}

        {/* Result */}
        {result && !loading && (
          <Alert
            variant={result.status === 'success' ? 'success' : 'error'}
            className="mb-6"
          >
            <div>
              <p className="font-semibold mb-2">
                {result.status === 'success' ? '✅ Demo Data Loaded!' : '❌ Error'}
              </p>
              <p className="text-sm mb-3">{result.message}</p>
              
              {result.status === 'success' && (
                <div className="bg-white/50 p-4 rounded text-sm">
                  <p className="mb-2">
                    <strong>Scenario:</strong> {result.scenario}
                  </p>
                  <p className="mb-3">
                    <strong>Signals Loaded:</strong> {result.signals_loaded}
                  </p>
                  
                  <div className="mb-3">
                    <p className="font-medium mb-2">Next Steps:</p>
                    <ol className="list-decimal ml-4 space-y-1">
                      {result.next_steps?.map((step: string, idx: number) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ol>
                  </div>

                  <div className="flex gap-3 mt-4">
                    <a
                      href="/signals"
                      className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
                    >
                      View Signals →
                    </a>
                    <a
                      href="/agent"
                      className="inline-block px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-sm"
                    >
                      Run Analysis →
                    </a>
                  </div>
                </div>
              )}
            </div>
          </Alert>
        )}

        {/* Instructions */}
        <Card className="p-6 bg-blue-50 border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-3">How to Use:</h3>
          <ol className="text-sm text-blue-800 space-y-2 list-decimal ml-4">
            <li><strong>Select a scenario</strong> above based on what you want to demonstrate</li>
            <li><strong>Click "Load This Scenario"</strong> to ingest the demo signals</li>
            <li><strong>View the signals</strong> in the Signals page to see what was loaded</li>
            <li><strong>Run analysis</strong> in the Agent page to see pattern detection</li>
            <li><strong>Approve actions</strong> to trigger real GitHub/Slack integrations (if configured)</li>
          </ol>
        </Card>

        <Card className="mt-6 p-6 bg-purple-50 border-purple-200">
          <h3 className="font-semibold text-purple-900 mb-3">💡 Demo Tips:</h3>
          <ul className="text-sm text-purple-800 space-y-2">
            <li>• <strong>Checkout Crisis</strong> - Best for showing high-risk escalation and GitHub integration</li>
            <li>• <strong>Webhook Issues</strong> - Good for medium-priority pattern detection</li>
            <li>• <strong>Mixed</strong> - Shows full capabilities with multiple patterns and priorities</li>
            <li>• Load data multiple times to see cumulative pattern detection</li>
            <li>• Reset by restarting the backend server</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
