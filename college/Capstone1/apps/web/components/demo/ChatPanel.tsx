"use client";

/* eslint-disable @next/next/no-img-element -- inline data-URI / object-URL images deliberately avoid next/image */

import { useEffect, useRef, useState } from "react";

import type { ChatMessage } from "@/lib/types";

interface ChatPanelProps {
  messages: ChatMessage[];
  busy: boolean;
  onSend: (text: string, photo?: File) => void;
}

function classNames(names: Record<string, boolean>): string {
  return Object.entries(names)
    .filter(([, on]) => on)
    .map(([name]) => name)
    .join(" ");
}

function InlineResult({ message }: { message: ChatMessage }) {
  if (!message.overlay_png_base64) return null;
  const classes = Object.values(message.classes_present ?? {});
  return (
    <div className="mt-3 space-y-2 rounded-xl bg-slate-900/70 p-3">
      <img
        src={`data:image/png;base64,${message.overlay_png_base64}`}
        alt="Model overlay of the detected damage"
        className="w-full rounded-lg border border-slate-700"
      />
      {classes.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {classes.map((name) => (
            <span
              key={name}
              className="rounded-full bg-amber-400/10 px-2.5 py-1 text-[11px] font-medium text-amber-300"
            >
              {name}
            </span>
          ))}
        </div>
      )}
      {message.low_confidence && (
        <p className="text-[11px] leading-relaxed text-amber-200/80">
          Low-confidence segmentation — treat the mask as preliminary. Model
          predictions only; not verified damage extent.
        </p>
      )}
    </div>
  );
}

export default function ChatPanel({ messages, busy, onSend }: ChatPanelProps) {
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const [draft, setDraft] = useState("");
  const [attachment, setAttachment] = useState<{ file: File; preview: string } | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

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

  return (
    <section className="flex h-full min-h-0 flex-col">
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto px-1 py-5">
        {messages.length === 0 && !busy && (
          <p className="rounded-xl bg-slate-800/60 px-4 py-3 text-sm leading-relaxed text-slate-300">
            Welcome. Attach a photo of the damaged area in the composer and hit
            send, or just describe what you see. I will run the image through the
            visual model and give you an honest read of the damage.
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={classNames({
              flex: true,
              "justify-end": m.role === "user",
              "justify-start": m.role === "assistant",
            })}
          >
            <div
              className={classNames({
                "max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed":
                  true,
                "rounded-br-md bg-amber-400 text-black": m.role === "user",
                "rounded-bl-md bg-slate-800 text-slate-100": m.role === "assistant",
              })}
            >
              {m.preview && (
                <img
                  src={m.preview}
                  alt="Attached photo"
                  className="mb-2 w-48 rounded-lg border border-slate-300/20"
                />
              )}
              {m.content}
              <InlineResult message={m} />
            </div>
          </div>
        ))}
        {busy && (
          <div className="flex justify-start">
            <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md bg-slate-800 px-4 py-3">
              <span className="h-2 w-2 animate-[pulse-soft_1.2s_ease-in-out_infinite] rounded-full bg-slate-400" />
              <span className="h-2 w-2 animate-[pulse-soft_1.2s_ease-in-out_0.2s_infinite] rounded-full bg-slate-400" />
              <span className="h-2 w-2 animate-[pulse-soft_1.2s_ease-in-out_0.4s_infinite] rounded-full bg-slate-400" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form
        onSubmit={submit}
        className="rounded-2xl border border-slate-700 bg-slate-900/80 p-2 focus-within:border-amber-400/50"
      >
        {attachment && (
          <div className="relative mb-2 inline-block">
            <img
              src={attachment.preview}
              alt="Attached photo preview"
              className="h-16 w-16 rounded-lg border border-slate-600 object-cover"
            />
            <button
              type="button"
              aria-label="Remove attached photo"
              onClick={clearAttachment}
              className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-slate-700 text-xs text-slate-200 transition hover:bg-rose-500"
            >
              ×
            </button>
          </div>
        )}
        <div className="flex items-center gap-2">
          <label
            aria-label="Attach a photo"
            className="flex h-9 w-9 shrink-0 cursor-pointer items-center justify-center rounded-full text-slate-400 transition hover:bg-slate-800 hover:text-slate-100"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="h-5 w-5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 8l3-3h12l3 3M3 8v11h18V8M3 8l4 4h10l4-4"
              />
            </svg>
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
          </label>
          <input
            ref={inputRef}
            type="text"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            disabled={busy}
            placeholder={busy ? "Working on it..." : "Ask or attach a photo of the damage"}
            className="min-w-0 flex-1 bg-transparent px-1 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={busy || (!draft.trim() && !attachment)}
            className="rounded-xl bg-amber-400 px-4 py-2 text-sm font-semibold text-black transition hover:bg-amber-300 disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </form>
    </section>
  );
}