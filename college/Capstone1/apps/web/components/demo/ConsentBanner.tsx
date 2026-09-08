"use client";

interface ConsentBannerProps {
  waitingFor: string | null;
  busy: boolean;
  onChoice: (granted: boolean) => void;
}

/** Optional training consent, always clearly labelled as optional. */
export default function ConsentBanner({ waitingFor, busy, onChoice }: ConsentBannerProps) {
  if (waitingFor !== "CONSENT") return null;
  return (
    <section className="rounded-2xl border border-slate-700 bg-slate-900/80 p-5">
      <h3 className="text-sm font-semibold text-slate-100">Help improve the model?</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-300">
        Completely optional. If you agree, this photo and the anonymised damage
        analysis are kept as a training sample. Decline and the photo is used only
        for this inspection and deleted when the session expires.
      </p>
      <div className="mt-4 flex gap-3">
        <button
          type="button"
          disabled={busy}
          onClick={() => onChoice(true)}
          className="flex-1 rounded-xl bg-emerald-400 px-4 py-3 text-sm font-semibold text-black transition hover:bg-emerald-300 disabled:opacity-40"
        >
          Yes, keep it for training
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onChoice(false)}
          className="flex-1 rounded-xl border border-slate-600 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:bg-slate-800 disabled:opacity-40"
        >
          No, thank you
        </button>
      </div>
    </section>
  );
}