"use client";

import type { InspectionStateView } from "@/lib/types";

interface ContextCardProps {
  insp: InspectionStateView | null;
}

const COMPARISON_LABELS: Record<string, string> = {
  AGREEMENT: "Agrees with the model",
  PARTIAL_AGREEMENT: "Partially agrees with the model",
  DISAGREEMENT: "Differs from the model",
  NOT_APPLICABLE: "No shared damage reported",
};

function Row({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div className="flex items-baseline justify-between gap-4 py-1.5">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-sm text-right font-medium text-slate-100 capitalize">{value}</span>
    </div>
  );
}

/** WHAT YOU TOLD US — the user-supplied inspection context with provenance. */
export default function ContextCard({ insp }: ContextCardProps) {
  if (!insp) return null;
  const hasContext = insp.incident || insp.damage_location || insp.repair_city;
  if (!hasContext) return null;

  const insurance =
    insp.insurance_claim === undefined ? "" : insp.insurance_claim ? "Yes" : "No";

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">What you told us</h3>
        <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] tracking-wide text-slate-400 uppercase">
          Provenance: user
        </span>
      </div>

      <div className="mt-2 divide-y divide-slate-800/70">
        <Row label="Incident" value={insp.incident ?? ""} />
        <Row label="Damage location" value={insp.damage_location ?? ""} />
        <Row label="Repair city" value={insp.repair_city ?? ""} />
        <Row label="Insurance claim" value={insurance} />
      </div>

      {insp.comparison && COMPARISON_LABELS[insp.comparison] && (
        <p
          className={`mt-3 rounded-xl px-3 py-2 text-xs font-medium ${
            insp.comparison === "AGREEMENT"
              ? "bg-emerald-500/10 text-emerald-300"
              : insp.comparison === "DISAGREEMENT"
                ? "bg-rose-500/10 text-rose-300"
                : "bg-amber-400/10 text-amber-200"
          }`}
        >
          {COMPARISON_LABELS[insp.comparison]}
        </p>
      )}
    </section>
  );
}