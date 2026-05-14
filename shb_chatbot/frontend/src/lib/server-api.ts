/**
 * Server-side API client for calling the FastAPI backend.
 * This module is used by Next.js API routes to proxy requests.
 * IMPORTANT: This file should only be imported in server-side code (API routes, Server Components).
 */

const BACKEND_URL = process.env.BACKEND_URL || "https://shbbot.onrender.com";

export class BackendApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(`Backend API error: ${status} ${statusText}`);
    this.name = "BackendApiError";
  }
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
  /** Return raw text instead of parsing as JSON */
  raw?: boolean;
}

/**
 * Make a request to the FastAPI backend.
 * This should only be called from Next.js API routes or Server Components.
 */
export async function backendFetch<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, body, raw, ...fetchOptions } = options;

  // Remove trailing slash from BACKEND_URL if present, and leading slash from endpoint
  const baseUrl = BACKEND_URL.endsWith("/") ? BACKEND_URL.slice(0, -1) : BACKEND_URL;
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  let url = `${baseUrl}${cleanEndpoint}`;

  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  // Determine content type - don't set for FormData (browser will set with boundary)
  const headers: Record<string, string> = {};
  if (body instanceof FormData) {
    // Let the browser set Content-Type with the multipart boundary
  } else {
    headers["Content-Type"] = "application/json";
  }

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers: {
        ...headers,
        ...fetchOptions.headers,
      },
      body: body && !(body instanceof FormData) ? JSON.stringify(body) : body as any,
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = null;
      }
      console.error(`Backend error ${response.status} at ${url}:`, errorData);
      throw new BackendApiError(response.status, response.statusText, errorData);
    }

    // Handle empty responses
    const text = await response.text();
    if (!text) {
      return null as T;
    }

    if (raw) {
      return text as T;
    }

    return JSON.parse(text);
  } catch (err) {
    if (err instanceof BackendApiError) throw err;
    
    console.error(`Fetch failed for ${url}:`, err);
    // Provide more context in the error
    throw new Error(`Failed to connect to backend at ${url}. Ensure BACKEND_URL is correct.`);
  }
}

/**
 * Forward authorization header from the incoming request to the backend.
 */
export function getAuthHeaders(
  authHeader: string | null
): Record<string, string> {
  if (!authHeader) {
    return {};
  }
  return { Authorization: authHeader };
}
