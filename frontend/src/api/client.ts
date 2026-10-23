/**
 * API client for the EduVerify AI backend.
 *
 * All functions return typed responses or throw an ApiError with a
 * human-readable message. The base URL is read from the Vite environment
 * variable VITE_API_BASE_URL (falls back to http://localhost:8000).
 */

import type {
  ApplicationDetailResponse,
  ApplicationListResponse,
  HealthResponse,
} from '../types'

// In development the Vite proxy forwards /api/* to the backend (see vite.config.ts).
// Set VITE_API_BASE_URL to an absolute URL only if deploying without the proxy.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? ''


export class ApiError extends Error {
  public readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}


async function get<T>(path: string): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
  } catch {
    throw new ApiError(0, 'Unable to reach the server. Is the backend running?')
  }

  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = await response.json()
      if (body?.detail) detail = body.detail
    } catch {
      // ignore parse failure
    }
    throw new ApiError(response.status, detail)
  }

  return response.json() as Promise<T>
}

export const api = {
  health(): Promise<HealthResponse> {
    return get<HealthResponse>('/api/health')
  },

  listApplications(): Promise<ApplicationListResponse> {
    return get<ApplicationListResponse>('/api/applications')
  },

  getApplication(id: string): Promise<ApplicationDetailResponse> {
    return get<ApplicationDetailResponse>(`/api/applications/${encodeURIComponent(id)}`)
  },
}
