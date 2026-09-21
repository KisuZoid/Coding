/// Types mirroring the backend contracts in apps/api/shared/schemas.py and the
/// inspection state serialised by apps/api/routers. Kept structurally aligned
/// with the API (they are the same JSON) so the two sides cannot drift.

export interface HealthResponse {
  status: "ok";
  service: string;
  environment: string;
  version: string;
}

export interface SessionCreated {
  session_id: string;
  status: string;
  created_at: string;
  expires_at: string;
}

export interface UploadResponse {
  session_id: string;
  asset_id: string;
  kind: string;
  note: string;
}

/** POST /inspection/{id}/analyze — photo-first, no cost/repair fields. */
export interface AnalyzeResponse {
  session_id: string;
  status: "OK" | "QUALITY_FAILED";
  assistant_message: string;
  asset_id: string;
  quality_status: string;
  quality_reasons: string[];
  inspection: InspectionPayload | null;
  classes_present: Record<string, string>;
  low_confidence: boolean;
  damage_fraction: number;
  mean_confidence: number;
  overlay_png_base64: string | null;
}

export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  request_id: string;
}

export interface ConsentResponse {
  session_id: string;
  decision: string;
  dataset_version: string;
  sample_id: string | null;
  saved: boolean;
  note: string;
}

/** The `inspection` dict written by POST /inspection/{id}/analyze. */
export interface InspectionPayload {
  classes_present: Record<string, string>;
  per_class_area_ratio_image: Record<string, number>;
  damage_area_ratio_image?: number;
  num_instances?: number;
  low_confidence?: boolean;
  low_confidence_instances?: number;
  mean_confidence?: number;
  damage_fraction?: number;
  width?: number;
  height?: number;
  quality?: { status: string; reasons: string[] };
  model_notes?: string[];
  model_metadata?: Record<string, unknown>;
}

export interface ChatMessage {
  role: string;
  content: string;
  /** Local thumbnail shown inside the user bubble for an attached photo. */
  preview?: string;
  /** Inline result attachment for an assistant analysis message. */
  overlay_png_base64?: string;
  quality_status?: string;
  classes_present?: Record<string, string>;
  low_confidence?: boolean;
}

/** The inspection state returned by GET /inspection/{id} (`state` field). */
export interface InspectionStateView {
  session_id: string;
  image_asset_id?: string;
  messages?: ChatMessage[];
  inspection?: InspectionPayload | null;
  quality?: { status: string; reasons: string[] };
  explanation?: string;
  consent?: string;
}

export interface InspectionStateResponse {
  session_id: string;
  status: string;
  state: InspectionStateView;
}