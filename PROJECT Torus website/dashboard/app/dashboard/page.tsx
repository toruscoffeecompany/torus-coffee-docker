'use client';

import { useEffect, useState } from 'react';

type ServiceStatus = {
  ok: boolean;
  account?: string;
  verified?: boolean;
  error?: string;
};

type StatusResponse = {
  timestamp: string;
  services: Record<string, ServiceStatus>;
};

export default function DashboardPage() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/api/status');
        if (!res.ok) throw new Error('Failed to load dashboard status');
        const data = (await res.json()) as StatusResponse;
        setStatus(data);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  return (
    <main className="min-h-screen bg-torus-darker text-gray-100 p-6">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Torus Coffee — Local Dashboard</h1>
            <p className="text-sm text-gray-400">
              Local network only • Not exposed to the public internet
            </p>
          </div>
          {status && (
            <div className="text-right text-xs text-gray-500">
              <div>Updated: {new Date(status.timestamp).toLocaleString()}</div>
              <div>Environment: local</div>
            </div>
          )}
        </header>

        {loading && <div className="text-gray-300">Loading dashboard…</div>}
        {error && <div className="text-red-400">Error: {error}</div>}

        {status && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            {Object.entries(status.services).map(([name, s]) => (
              <div
                key={name}
                className="rounded-lg border border-torus-border bg-torus-card p-4"
              >
                <div className="mb-2 flex items-center justify-between">
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-300">
                    {name}
                  </h2>
                  <span
                    className={
                      'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ' +
                      (s.ok
                        ? 'bg-emerald-900/40 text-emerald-300'
                        : 'bg-red-900/40 text-red-300')
                  }
                  >
                    {s.ok ? 'Connected' : 'Issue'}
                  </span>
                </div>
                <div className="space-y-1 text-sm">
                  {s.account && (
                    <div className="text-gray-400">Account: {s.account}</div>
                  )}
                  {s.verified !== undefined && (
                    <div className="text-gray-400">
                      Verified: {s.verified ? 'Yes' : 'No'}
                    </div>
                  )}
                  {s.error && <div className="text-red-400">{s.error}</div>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
