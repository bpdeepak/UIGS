/**
 * API Client for Ingestion Service
 */

const INGESTION_URL = process.env.NEXT_PUBLIC_INGESTION_URL || 'http://localhost:8081';

export interface IngestRequest {
  source_type: 'VC' | 'OIDC' | 'MANUAL';
  payload: Record<string, unknown>;
}

export interface IngestResponse {
  event_id: string;
  status: string;
  message: string;
  created_at: string;
}

export async function ingestCredential(data: IngestRequest): Promise<IngestResponse> {
  const response = await fetch(`${INGESTION_URL}/api/v1/ingest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${INGESTION_URL}/health`);
  return response.json();
}
