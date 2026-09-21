"use client";

interface ConsentBannerProps {
  visible: boolean;
  busy: boolean;
  onChoice: (granted: boolean) => void;
}

/** Optional training consent, always clearly labelled as optional. */
export default function ConsentBanner({ visible, busy, onChoice }: ConsentBannerProps) {
  if (!visible) return null;
  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <h3 className="text-sm font-semibold text-slate-100">Help improve the model?</h3>
      <p className="mt-1.5 text-xs leading-relaxed text-slate-400">
        Completely optional. If you agree, this photo and the anonymised damage
        analysis are kept as a training sample. Decline and the photo is used only
        for this inspection and deleted when the session expires.
      </p>
      <div className="mt-3 flex flex-col gap-2 sm:flex-row">
        <button
          type="button"
          disabled={busy}
          onClick={() => onChoice(true)}
          className="flex-1 rounded-lg border border-emerald-400/20 bg-emerald-400/15 px-4 py-2 text-sm font-semibold text-emerald-200 transition hover:bg-emerald-400/25 disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/60"
        >
          Yes, keep it for training
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onChoice(false)}
          className="flex-1 rounded-lg border border-white/10 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:bg-white/5 disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/60"
        >
          No, thank you
        </button>
      </div>
    </section>
  );
}