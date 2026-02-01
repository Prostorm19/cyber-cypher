'use client';

import { useState } from 'react';
import { Card, Alert, LoadingSpinner } from '@/components/ui';

export default function SignalUploadPage() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await uploadFile(e.target.files[0]);
    }
  };

  const uploadFile = async (file: File) => {
    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const endpoint = file.name.endsWith('.csv')
        ? '/signals/upload/csv'
        : '/signals/upload/json';

      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = () => {
    const csvContent = `timestamp,signal_type,merchant_id,migration_stage,description,severity,category
2026-02-01T06:00:00Z,checkout_issue,merchant_001,mid_migration,Checkout page blank,high,checkout
2026-02-01T06:05:00Z,error_log,merchant_002,mid_migration,Auth token invalid,high,checkout`;

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'signal_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Signals</h1>
          <p className="text-gray-600">
            Upload CSV or JSON files containing signals for analysis
          </p>
        </div>

        {/* Template Download */}
        <Card className="mb-6 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold mb-1">Need a template?</h2>
              <p className="text-sm text-gray-600">
                Download a CSV template with the correct format
              </p>
            </div>
            <button
              onClick={downloadTemplate}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Download Template
            </button>
          </div>
        </Card>

        {/* Upload Area */}
        <Card className="p-8">
          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 bg-white hover:border-gray-400'
              }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {uploading ? (
              <div className="flex flex-col items-center">
                <LoadingSpinner />
                <p className="mt-4 text-gray-600">Uploading and processing...</p>
              </div>
            ) : (
              <>
                <svg
                  className="mx-auto h-16 w-16 text-gray-400 mb-4"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Drop your CSV or JSON file here
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  or click to browse
                </p>
                <input
                  type="file"
                  accept=".csv,.json"
                  onChange={handleFileInput}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer inline-flex px-6 py-3 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Select File
                </label>
                <p className="mt-4 text-xs text-gray-500">
                  Supported formats: CSV, JSON
                </p>
              </>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <Alert variant="error" className="mt-6">
              <strong>Error:</strong> {error}
            </Alert>
          )}

          {/* Success Display */}
          {result && (
            <Alert variant="success" className="mt-6">
              <div>
                <p className="font-semibold mb-2">✅ Upload Successful!</p>
                <p className="text-sm mb-3">{result.message}</p>
                <div className="bg-white/50 p-3 rounded text-sm">
                  <p><strong>File:</strong> {result.filename}</p>
                  <p><strong>Signals Ingested:</strong> {result.signal_ids?.length || 0}</p>
                  {result.signal_ids && result.signal_ids.length > 0 && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-blue-600 hover:text-blue-700">
                        View Signal IDs
                      </summary>
                      <ul className="mt-2 ml-4 text-xs space-y-1">
                        {result.signal_ids.map((id: string, idx: number) => (
                          <li key={idx}>• {id}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                </div>
                <a
                  href="/"
                  className="inline-block mt-4 text-sm text-blue-600 hover:text-blue-700"
                >
                  ← Back to Dashboard
                </a>
              </div>
            </Alert>
          )}
        </Card>

        {/* Instructions */}
        <Card className="mt-6 p-6 bg-blue-50 border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-3">CSV Format Requirements:</h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>• <strong>timestamp</strong>: ISO 8601 format (e.g., 2026-02-01T06:00:00Z)</li>
            <li>• <strong>signal_type</strong>: support_ticket, error_log, checkout_issue, api_error, webhook_failure, migration_event</li>
            <li>• <strong>merchant_id</strong>: Unique merchant identifier</li>
            <li>• <strong>migration_stage</strong>: pre_migration, mid_migration, post_migration, completed</li>
            <li>• <strong>description</strong>: Detailed description of the issue</li>
            <li>• <strong>severity</strong>: low, medium, high, critical</li>
            <li>• <strong>category</strong>: checkout, payment, webhook, general, etc.</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
