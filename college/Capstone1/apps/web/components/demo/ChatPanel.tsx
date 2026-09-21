"use client";

/* eslint-disable @next/next/no-img-element -- inline data-URI / object-URL images deliberately avoid next/image */

import { useEffect, useRef, useState } from "react";
import { type ReactNode } from "react";

import BrandMark from "@/components/demo/BrandMark";
import type { ChatMessage } from "@/lib/types";

interface ChatPanelProps {
  messages: ChatMessage[];
  busy: boolean;
  onSend: (text: string, photo?: File) => void;
  /** Content rendered inside the conversation after the messages (consent, disclaimer...). */
  footer?: ReactNode;
  /** Friendly display notice surfaced in the conversation (session/API errors). */
  notice?: string | null;
  apiOffline?: boolean;
}

const QUALITY_REASONS_FALLBACK = [
  "the damaged area in focus",
  "enough surrounding vehicle context",
  "better lighting",
];

// Shared readable cap for both user and assistant message content. Matches the
// conversation column max-width so each message (text and analysis block)
// aligns to one consistent edge; rows are full-width wrappers that align right
// (user) / left (assistant) inside the shell.
const MESSAGE_MAX_WIDTH = "max-w-[46rem]";

function Message({ message, onRetake }: { message: ChatMessage; onRetake: () => void }) {
  if (message.role === "user") {
    return (
      <div data-message-role="user" className="msg-in flex justify-end">
        <div
          className={`${MESSAGE_MAX_WIDTH} min-w-0 rounded-2xl rounded-br-md bg-amber-400 px-4 py-2.5 text-sm leading-relaxed text-black`}
        >
          {message.preview && (
            <img
              src={message.preview}
              alt="Attached photo"
              className="mb-2 max-h-56 w-auto max-w-full rounded-xl border border-black/10 object-cover"
            />
          )}
          <span className="whitespace-pre-wrap">{message.content}</span>
        </div>
      </div>
    );
  }

  return (
    <div data-message-role="assistant" className="msg-in flex justify-start">
      <div
        className={`${MESSAGE_MAX_WIDTH} w-full min-w-0 rounded-2xl bg-blue-900/70 px-4 py-3`}
      >
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-200">
          {message.content}
        </p>
        {message.overlay_png_base64 ? (
          <AnalysisBlock message={message} />
        ) : message.quality_status && message.quality_status !== "OK" ? (
          <QualityBlock message={message} onRetake={onRetake} />
        ) : null}
      </div>
    </div>
  );
}

function AnalysisBlock({ message }: { message: ChatMessage }) {
  const classes = Object.values(message.classes_present ?? {});
  const confidence = message.mean_confidence;
  const fraction = message.damage_fraction;
  const rows: Array<[string, string]> = [
    ["Detected region", classes.length ? classes.join(" · ") : "None above threshold"],
  ];
  if (confidence !== undefined && Number.isFinite(confidence)) {
    rows.push(["Mean confidence", `${(confidence * 100).toFixed(1)}%`]);
  }
  if (fraction !== undefined && Number.isFinite(fraction)) {
    rows.push(["Damage area", `${(fraction * 100).toFixed(1)}% of image`]);
  }

  return (
    <div className="mt-4 w-full space-y-3">
      <p className="text-[10px] font-semibold tracking-[0.22em] text-amber-300/90 uppercase">
        Model finding
      </p>
      <img
        src={`data:image/png;base64,${message.overlay_png_base64}`}
        alt="Model overlay of the detected damage"
        className="max-h-[26rem] w-full max-w-[30rem] rounded-2xl border border-white/10 bg-black/50 object-contain"
      />
      {classes.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold tracking-[0.18em] text-slate-500 uppercase">
            Detected damage
          </p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {classes.map((name) => (
              <span
                key={name}
                className="rounded-full border border-amber-400/20 bg-amber-400/10 px-2.5 py-0.5 text-[11px] font-medium text-amber-200"
              >
                {name}
              </span>
            ))}
          </div>
        </div>
      )}
      {rows.length > 1 && (
        <div>
          <p className="text-[10px] font-semibold tracking-[0.18em] text-slate-500 uppercase">
            Inspection details
          </p>
          <dl className="mt-1.5 divide-y divide-white/5 rounded-xl border border-white/5 bg-white/[0.03] px-4">
            {rows.map(([label, value]) => (
              <div key={label} className="flex items-baseline justify-between gap-6 py-2">
                <dt className="text-xs text-slate-400">{label}</dt>
                <dd className="text-right text-xs font-medium text-slate-100">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
      {message.low_confidence && (
        <p className="rounded-xl border border-amber-400/20 bg-amber-400/[0.06] px-3 py-2 text-[11px] leading-relaxed text-amber-200/80">
          Low-confidence segmentation — treat the mask as preliminary. Model
          predictions only; not verified damage extent.
        </p>
      )}
    </div>
  );
}

function QualityBlock({ message, onRetake }: { message: ChatMessage; onRetake: () => void }) {
  const reasons = message.quality_reasons?.length ? message.quality_reasons : QUALITY_REASONS_FALLBACK;
  return (
    <div className="mt-4 w-full space-y-2.5 rounded-xl border border-amber-400/20 bg-amber-400/[0.05] p-4">
      <p className="text-[10px] font-semibold tracking-[0.22em] text-amber-300/90 uppercase">
        Photo quality
      </p>
      <p className="text-[13px] leading-relaxed text-slate-300">
        This photo isn&rsquo;t clear enough for a reliable inspection. Please retake it with:
      </p>
      <ul className="list-disc space-y-1 pl-5 text-[13px] leading-relaxed text-slate-300">
        {reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
      <button
        type="button"
        onClick={onRetake}
        className="mt-1 inline-flex items-center gap-1.5 rounded-full border border-amber-400/30 bg-amber-400/10 px-3.5 py-1.5 text-xs font-semibold text-amber-200 transition hover:bg-amber-400/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/60"
      >
        Retake photo
      </button>
    </div>
  );
}

function EmptyState({ onAttach }: { onAttach: () => void }) {
  return (
    <div className="m-auto flex max-w-sm flex-col items-center py-12 text-center">
      <BrandMark className="h-10 w-10 text-amber-400" />
      <h2 className="mt-4 text-lg font-semibold text-slate-100">AutoInspect-X</h2>
      <p className="mt-1.5 text-sm text-slate-400">
        Vehicle damage inspection, powered by computer vision.
      </p>
      <p className="mt-1 text-sm text-slate-500">Upload a clear photo of the damage to begin.</p>
      <button
        type="button"
        onClick={onAttach}
        className="mt-6 inline-flex items-center gap-2 rounded-full border border-amber-400/30 bg-amber-400/10 px-5 py-2.5 text-sm font-semibold text-amber-200 transition hover:bg-amber-400/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/60"
      >
        <PaperclipIcon className="h-4 w-4" />
        Attach photo
      </button>
    </div>
  );
}

function Loading({ analyzing }: { analyzing: boolean }) {
  return (
    <div className="msg-in flex items-center gap-3 py-1" role="status" aria-live="polite">
      <span className="flex items-center gap-1" aria-hidden>
        <span className="h-1.5 w-1.5 animate-[pulse-soft_1.2s_ease-in-out_infinite] rounded-full bg-slate-500" />
        <span className="h-1.5 w-1.5 animate-[pulse-soft_1.2s_ease-in-out_0.2s_infinite] rounded-full bg-slate-500" />
        <span className="h-1.5 w-1.5 animate-[pulse-soft_1.2s_ease-in-out_0.4s_infinite] rounded-full bg-slate-500" />
      </span>
      <span className="text-sm text-slate-400">
        {analyzing ? "Analyzing the submitted vehicle image…" : "Thinking…"}
      </span>
    </div>
  );
}

function Notice({ children }: { children: ReactNode }) {
  return (
    <div className="mb-3 flex items-start gap-2 rounded-xl border border-amber-400/20 bg-amber-400/[0.05] px-3.5 py-2.5 text-xs leading-relaxed text-amber-200/90">
      <span className="mt-px shrink-0" aria-hidden>
        ⚠
      </span>
      <span>{children}</span>
    </div>
  );
}

function PaperclipIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      className={className}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3 8l3-3h12l3 3M3 8v11h18V8M3 8l4 4h10l4-4"
      />
    </svg>
  );
}

function SendIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      className={className}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4.5 12h13M13 6.5 18.5 12 13 17.5"
      />
    </svg>
  );
}

export default function ChatPanel({ messages, busy, onSend, footer, notice, apiOffline }: ChatPanelProps) {
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const scrollerRef = useRef<HTMLDivElement>(null);
  const nearBottomRef = useRef(true);
  const [draft, setDraft] = useState("");
  const [attachment, setAttachment] = useState<{ file: File; preview: string } | null>(null);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    if (nearBottomRef.current) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [messages, busy]);

  const handleScroll = () => {
    const el = scrollerRef.current;
    if (!el) return;
    nearBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
  };

  const pickAttachment = (file: File | undefined) => {
    if (!file || busy) return;
    const preview = URL.createObjectURL(file);
    setAttachment((old) => {
      if (old) URL.revokeObjectURL(old.preview);
      return { file, preview };
    });
  };

  const clearAttachment = () => {
    setAttachment((old) => {
      if (old) URL.revokeObjectURL(old.preview);
      return null;
    });
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (busy) return;
    const text = draft.trim();
    if (!text && !attachment) return;
    onSend(text, attachment?.file);
    setDraft("");
    clearAttachment();
    inputRef.current?.focus();
  };

  const openFilePicker = () => {
    if (!busy) fileRef.current?.click();
  };

  const last = messages[messages.length - 1];
  const analyzing = busy && last?.role === "user" && (!!last.preview || last.content.startsWith("[Photo attached]"));
  const empty = messages.length === 0 && !busy;

  return (
    <section className="flex min-h-0 flex-1 flex-col">
      <div ref={scrollerRef} onScroll={handleScroll} className="chat-scroll min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto flex min-h-full w-full max-w-[46rem] flex-col px-4 py-4 sm:px-6 sm:py-5">
          {apiOffline && (
            <Notice>
              The AutoInspect-X API is not reachable. Start the backend (uvicorn
              apps.api.main:app in the ai conda environment) and reload this page.
            </Notice>
          )}
          {notice && <Notice>{notice}</Notice>}

          {empty ? (
            <EmptyState onAttach={openFilePicker} />
          ) : (
            <div className="flex flex-col gap-5">
              {messages.map((m, i) => (
                <Message key={i} message={m} onRetake={openFilePicker} />
              ))}
            </div>
          )}

          {busy && messages.length > 0 && <Loading analyzing={analyzing} />}
          {footer}
          <div ref={endRef} className="h-3 shrink-0" />
        </div>
      </div>

      <div className="flex-none px-4 pb-3 pt-1 sm:px-6 sm:pb-4 sm:pt-2">
        <form
          onSubmit={submit}
          className="mx-auto w-full max-w-[52rem] rounded-2xl border border-white/10 bg-[#11171e] shadow-xl shadow-black/30 transition-colors focus-within:border-amber-400/40"
        >
          {attachment && (
            <div className="flex items-center gap-3 border-b border-white/5 px-3 py-2.5 sm:px-4">
              <img
                src={attachment.preview}
                alt="Attached photo preview"
                className="h-14 w-14 shrink-0 rounded-lg border border-white/10 object-cover"
              />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-100">
                  {attachment.file.name}
                </p>
                <p className="text-[11px] text-emerald-300/90">
                  Photo attached — ready to analyze
                </p>
              </div>
              <button
                type="button"
                aria-label="Remove attached photo"
                onClick={clearAttachment}
                className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-slate-400 transition hover:bg-rose-500/20 hover:text-rose-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400/60"
              >
                ×
              </button>
            </div>
          )}
          <div className="flex items-center gap-2 px-2 py-2 sm:px-3">
            <button
              type="button"
              aria-label="Attach a photo"
              disabled={busy}
              onClick={openFilePicker}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-slate-400 transition hover:bg-white/5 hover:text-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/60 disabled:opacity-40"
            >
              <PaperclipIcon className="h-5 w-5" />
            </button>
            <input
              ref={inputRef}
              type="text"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              disabled={busy}
              placeholder={busy ? "Working on it…" : "Ask or attach a photo of the damage"}
              aria-label="Chat message"
              className="min-w-0 flex-1 bg-transparent px-1 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={busy || (!draft.trim() && !attachment)}
              className="inline-flex items-center gap-1.5 rounded-xl bg-amber-400 px-4 py-2 text-sm font-semibold text-black transition hover:bg-amber-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/60 disabled:opacity-40"
            >
              <SendIcon className="h-4 w-4" />
              Send
            </button>
          </div>
        </form>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          disabled={busy}
          className="hidden"
          onChange={(e) => {
            pickAttachment(e.target.files?.[0]);
            e.target.value = "";
          }}
        />
      </div>
    </section>
  );
}