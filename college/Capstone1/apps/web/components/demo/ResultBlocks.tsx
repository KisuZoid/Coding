"use client";

import type { AnalysisPayload, CostPayload, InspectionStateView, RepairPayload } from "@/lib/types";

interface ResultBlocksProps {
  insp: InspectionStateView | null;
  analysing: boolean;
}

function Block({
  tone,
  title,
  provenance,
  children,
}: {
  tone: "slate" | "amber" | "emerald" | "sky";
  title: string;
  provenance: string;
  children: React.ReactNode;
}) {
  const ring =
    tone === "amber"
      ? "border-amber-400/40"
      : tone === "emerald"
        ? "border-emerald-400/40"
        : tone === "sky"
          ? "border-sky-400/40"
          : "border-slate-700";
  return (
    <section className={`rounded-2xl border ${ring} bg-slate-900/70 p-5`}>
      <div className="flex items-center justify-between gap-3">
        <h3 className={`text-sm font-semibold ${tone === "amber" ? "text-amber-300" : "text-slate-100"}`}>
          {title}
        </h3>
        <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] tracking-wide text-slate-400 uppercase">
          {provenance}
        </span>
      </div>
      <div className="mt-3 text-sm leading-relaxed text-slate-300">{children}</div>
    </section>
  );
}

function areaPercent(analysis: AnalysisPayload): string {
  const ratio =
    analysis.damage_area_ratio_image ?? analysis.damage_fraction ?? analysis.features?.damage_area_ratio_image;
  if (typeof ratio !== "number") return "—";
  return `${(ratio * 100).toFixed(2)} % of the image`;
}

function CostBlock({ cost }: { cost: CostPayload | undefined }) {
  if (!cost) return null;
  const status = cost.status ?? "DATA_UNAVAILABLE";
  if (status === "SYNTHETIC_ESTIMATE" && cost.p50) {
    return (
      <Block tone="amber" title="What we estimate" provenance="Synthetic demo">
        <p className="font-semibold text-amber-200">
          {cost.p50.amount.toLocaleString(undefined, {
            style: "currency",
            currency: cost.p50.currency,
            maximumFractionDigits: 0,
          })}
          <span className="ml-2 text-xs font-normal text-amber-200/70">
            (range {cost.p10?.amount.toLocaleString(undefined, { style: "currency", currency: cost.p10?.currency, maximumFractionDigits: 0 }) ?? "—"} –{" "}
            {cost.p90?.amount.toLocaleString(undefined, { style: "currency", currency: cost.p90?.currency, maximumFractionDigits: 0 }) ?? "—"})
          </span>
        </p>
        <p className="mt-2 rounded-lg bg-amber-400/10 px-3 py-2 text-xs font-semibold text-amber-200">
          {cost.synthetic_label ?? "DEMO / SYNTHETIC ESTIMATE — NOT A REAL QUOTE"}
        </p>
        <p className="mt-3">{cost.explanation}</p>
      </Block>
    );
  }
  return (
    <Block tone="sky" title="What we estimate" provenance="System">
      <p className="font-semibold text-sky-200">No real quote is available.</p>
      <p className="mt-2">{cost.explanation}</p>
    </Block>
  );
}

function RepairBlock({ repair }: { repair: RepairPayload | undefined }) {
  if (!repair?.action) return null;
  return (
    <Block tone="emerald" title="What we recommend" provenance="Demo rule">
      <p className="font-semibold text-emerald-200 capitalize">{repair.action.toLowerCase().replace("_", " ")}</p>
      <p className="mt-2 text-xs text-slate-400">
        {repair.rule ?? "Preliminary demonstration rule"}
      </p>
      <p className="mt-2">{repair.reason}</p>
    </Block>
  );
}

/** Phase N: the four labelled result blocks + overlay + low-confidence banner. */
export default function ResultBlocks({ insp, analysing }: ResultBlocksProps) {
  if (!insp) return null;

  if (analysing) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
        <h3 className="text-sm font-semibold text-slate-200">Running the analysis</h3>
        <div className="mt-4 space-y-2">
          <div className="analysis-shimmer h-3 rounded-full" />
          <div className="analysis-shimmer h-3 w-11/12 rounded-full" />
          <div className="analysis-shimmer h-3 w-4/6 rounded-full" />
        </div>
        <ul className="mt-4 space-y-1.5 text-xs text-slate-400">
          <li>Reading damage regions from the segmentation model</li>
          <li>Extracting features and confidence</li>
          <li>Comparing what you reported with what was found</li>
          <li>Checking repair and cost honesty rules</li>
        </ul>
      </section>
    );
  }

  const analysis = insp.analysis;
  if (!analysis) return null;

  const classes = analysis.classes_present ?? analysis.model_classes ?? {};
  const overlap = insp.image_asset_id && analysis.overlay_png_base64;

  return (
    <div className="space-y-4">
      {analysis.low_confidence && (
        <div className="rounded-2xl border border-amber-400/50 bg-amber-400/10 p-4 text-sm text-amber-200">
          <p className="font-semibold">Low confidence</p>
          <p className="mt-1 leading-relaxed">
            The demonstration model is not confident in this reading. Treat the
            findings below as a hint, not a verified assessment.
          </p>
        </div>
      )}

      <Block tone="slate" title="What the model found" provenance="Model prediction">
        <div className="flex flex-wrap gap-2">
          {Object.values(classes).length ? (
            Object.entries(classes).map(([id, name]) => (
              <span key={id} className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-100 capitalize">
                {name}
              </span>
            ))
          ) : (
            <span className="text-xs text-slate-400">No damage regions clearly visible</span>
          )}
        </div>
        <dl className="mt-3 space-y-1 text-xs text-slate-400">
          <div className="flex justify-between">
            <dt>Damage area</dt>
            <dd className="text-slate-200">{areaPercent(analysis)}</dd>
          </div>
          <div className="flex justify-between">
            <dt>Mean confidence</dt>
            <dd className="text-slate-200">
              {typeof analysis.mean_confidence === "number"
                ? `${(analysis.mean_confidence * 100).toFixed(1)} %`
                : "—"}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt>Damage regions found</dt>
            <dd className="text-slate-200">{analysis.num_instances ?? 0}</dd>
          </div>
        </dl>
        {overlap && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`data:image/png;base64,${analysis.overlay_png_base64}`}
            alt="Predicted damage overlaid on the photo"
            className="mt-4 w-full rounded-xl"
          />
        )}
        <p className="mt-3 text-xs text-slate-500">
          Image-denominator area only (no part segmentation); this is the model
          prediction, not verified ground truth.
        </p>
      </Block>

      <CostBlock cost={insp.cost} />
      <RepairBlock repair={insp.repair} />
    </div>
  );
}