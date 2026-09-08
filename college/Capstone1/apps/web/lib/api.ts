/// Typed HTTP client for the AutoInspect-X API (mirrors apps/api routers).
/// The base URL comes from NEXT_PUBLIC_API_URL (set per environment); the
/// backend grants CORS only to its configured origins.

import type {
  AnalyzeResponse,
  ChatResponse,
  ConsentResponse,
  HealthResponse,
  InspectionStateResponse,
  SessionCreated,
  UploadResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...init?.headers,
      },
    });
  } catch {
    throw new ApiError(
      `Cannot reach the inspection API at ${API_BASE}. Is the backend running?`,
      0,
    );
  }

  if (!response.ok) {
    let body: unknown;
    let detail = `Request failed (${response.status})`;
    try {
      body = await response.json();
      const detailField = (body as { detail?: unknown }).detail;
      detail = typeof detailField === "string" ? detailField : JSON.stringify(detailField);
    } catch {
      /* keep the fallback message */
    }
    throw new ApiError(detail, response.status, body);
  }
  return (await response.json()) as T;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function createSession(): Promise<SessionCreated> {
  return request<SessionCreated>("/inspection/session", { method: "POST" });
}

export function getInspection(sessionId: string): Promise<InspectionStateResponse> {
  return request<InspectionStateResponse>(`/inspection/${sessionId}`);
}

export function deleteInspection(sessionId: string): Promise<{ session_id: string; status: string }> {
  return request<{ session_id: string; status: string }>(`/inspection/${sessionId}`, {
    method: "DELETE",
  });
}

export async function uploadPhoto(sessionId: string, file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  return request<UploadResponse>(`/inspection/${sessionId}/upload`, { method: "POST", body: form });
}

export function analyzePhoto(sessionId: string): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>(`/inspection/${sessionId}/analyze`, { method: "POST" });
}

export async function sendChat(sessionId: string, message: string): Promise<ChatResponse> {
  return request<ChatResponse>(`/chat`, {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, message }),
  });
}

export function sendConsent(
  sessionId: string,
  decision: "GRANTED" | "DECLINED",
): Promise<ConsentResponse> {
  return request<ConsentResponse>(`/inspection/${sessionId}/consent`, {
    method: "POST",
    body: JSON.stringify({ decision }),
  });
}