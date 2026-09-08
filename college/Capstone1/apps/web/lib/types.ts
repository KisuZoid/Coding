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

export interface AnalyzeResponse {
  session_id: string;
  asset_id: string;
  low_confidence: boolean;
  damage_fraction: number;
  mean_confidence: number;
  classes_present: Record<string, string>;
  analysis: AnalysisPayload;
  overlay_png_base64: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  waiting_for: string | null;
  finished: boolean;
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

/** Shape of the `analysis` dict written by POST /inspection/{id}/analyze. */
export interface AnalysisPayload {
  classes_present?: Record<string, string>;
  model_classes?: Record<string, string>;
  damage_fraction?: number;
  mean_confidence?: number;
  low_confidence?: boolean;
  per_class_area_ratio_image?: Record<string, number>;
  num_instances?: number;
  low_confidence_instances?: number;
  width?: number;
  height?: number;
  damage_area_ratio_image?: number;
  features?: Record<string, unknown>;
  overlay_png_base64?: string;
}

export interface RepairPayload {
  action?: string;
  rule?: string;
  reason?: string;
}

export interface CostPayload {
  status?: string;
  explanation?: string;
  is_synthetic_demo?: boolean;
  synthetic_label?: string | null;
  p10?: { amount: number; currency: string } | null;
  p50?: { amount: number; currency: string } | null;
  p90?: { amount: number; currency: string } | null;
}

export interface ChatMessage {
  role: string;
  content: string;
}

/** The inspection state returned by GET /inspection/{id} (`state` field). */
export interface InspectionStateView {
  session_id: string;
  incident?: string;
  damage_location?: string;
  repair_city?: string;
  insurance_claim?: boolean;
  optional_cursor?: number;
  waiting_for?: string | null;
  halt?: boolean;
  finished?: boolean;
  consent?: string;
  comparison?: string;
  image_asset_id?: string;
  messages?: ChatMessage[];
  analysis?: AnalysisPayload;
  feature_summary?: Record<string, unknown>;
  repair?: RepairPayload;
  cost?: CostPayload;
  model_classes?: Record<string, string>;
}

export interface InspectionStateResponse {
  session_id: string;
  status: string;
  state: InspectionStateView;
}