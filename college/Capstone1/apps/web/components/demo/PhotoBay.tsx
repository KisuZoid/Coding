"use client";

import { useRef, useState } from "react";

interface PhotoBayProps {
  waitingFor: string | null;
  hasImage: boolean;
  busy: boolean;
  phase: "ask" | "upload" | "analysing" | "retake" | "done";
  rejectReason?: string | null;
  onFile: (file: File) => void;
}

/**
 * Photo guidance + upload + validation UX. The backend owns validation (type /
 * size / EXIF strip / quality); this panel surfaces its states and asks for a
 * retake when the analysis loop requests one.
 */
export default function PhotoBay({
  waitingFor,
  hasImage,
  busy,
  phase,
  rejectReason = null,
  onFile,
}: PhotoBayProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const pick = (file: File | undefined) => {
    if (!file || busy) return;
    const url = URL.createObjectURL(file);
    setPreview((old) => {
      if (old) URL.revokeObjectURL(old);
      return url;
    });
    onFile(file);
  };

  const active = waitingFor === "PHOTO" || hasImage;
  if (!active) return null;

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <h3 className="text-sm font-semibold text-slate-200">Photo of the damage</h3>

      {phase === "upload" || phase === "analysing" ? (
        preview ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={preview}
            alt="Uploaded preview"
            className="mt-4 max-h-64 w-full rounded-xl object-cover"
          />
        ) : null
      ) : null}

      {phase === "upload" && (
        <p className="mt-3 text-sm leading-relaxed text-slate-300">
          Uploaded and stored for this session only. Running the analysis engine now.
        </p>
      )}

      {phase === "analysing" && (
        <div className="mt-4 space-y-2">
          <div className="analysis-shimmer h-3 w-3/4 rounded-full" />
          <div className="analysis-shimmer h-3 w-1/2 rounded-full" />
          <p className="text-xs text-slate-400">Analysing damage regions and confidence.</p>
        </div>
      )}

      {phase === "retake" && (
        <p className="mt-3 rounded-xl bg-amber-400/10 px-4 py-3 text-sm leading-relaxed text-amber-200">
          {rejectReason ??
            "Your photo was rejected — please retake it in better light, close up, clear of glare, and holding the phone steady."}
        </p>
      )}

      {phase === "done" && (
        <p className="mt-3 text-sm leading-relaxed text-slate-300">
          Photo analysed. The results panel below shows what the model found.
        </p>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(e) => pick(e.target.files?.[0])}
      />

      {!hasImage && (
        <button
          type="button"
          disabled={busy}
          onClick={() => inputRef.current?.click()}
          className="mt-4 w-full rounded-xl border border-dashed border-amber-400/60 bg-amber-400/5 px-4 py-6 text-sm font-medium text-amber-300 transition hover:bg-amber-400/10 disabled:opacity-50"
        >
          {busy ? "Working..." : "Choose a photo or tap to open camera"}
        </button>
      )}
      {hasImage && (
        <button
          type="button"
          disabled={busy}
          onClick={() => inputRef.current?.click()}
          className="mt-3 text-xs font-medium text-slate-400 hover:text-slate-200"
        >
          Replace photo
        </button>
      )}
    </section>
  );
}