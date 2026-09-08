"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage } from "@/lib/types";

interface ChatPanelProps {
  messages: ChatMessage[];
  busy: boolean;
  disabled?: boolean;
  onSend: (text: string) => void;
}

export default function ChatPanel({ messages, busy, disabled, onSend }: ChatPanelProps) {
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const value = inputRef.current?.value.trim();
    if (!value || busy || disabled) return;
    onSend(value);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <section className="flex h-full min-h-0 flex-col rounded-2xl border border-slate-800 bg-slate-900/60">
      <div className="border-b border-slate-800 px-5 py-3 text-sm font-semibold text-slate-200">
        AutoInspect-X assistant
      </div>

      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-5">
        {messages.length === 0 && !busy && (
          <p className="rounded-xl bg-slate-800/60 px-4 py-3 text-sm leading-relaxed text-slate-300">
            Welcome. Describe what happened to your vehicle in plain words, and I
            will guide you through a photo and a clear, honest read of the damage.
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-amber-400 text-black"
                  : "bg-slate-800 text-slate-100"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {busy && (
          <div className="flex justify-start">
            <div className="flex items-center gap-1.5 rounded-2xl bg-slate-800 px-4 py-3">
              <span className="h-2 w-2 animate-[pulse-soft_1.2s_ease-in-out_infinite] rounded-full bg-slate-400" />
              <span className="h-2 w-2 animate-[pulse-soft_1.2s_ease-in-out_0.2s_infinite] rounded-full bg-slate-400" />
              <span className="h-2 w-2 animate-[pulse-soft_1.2s_ease-in-out_0.4s_infinite] rounded-full bg-slate-400" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3 border-t border-slate-800 p-4">
        <input
          ref={inputRef}
          type="text"
          disabled={busy || disabled}
          placeholder={
            busy ? "Working on it..." : disabled ? "Inspection finished" : "Type your reply"
          }
          className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-800/70 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:border-amber-400/60 focus:outline-none disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={busy || disabled}
          className="rounded-xl bg-amber-400 px-5 text-sm font-semibold text-black transition hover:bg-amber-300 disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </section>
  );
}