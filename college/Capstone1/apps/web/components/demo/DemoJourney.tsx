"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import BrandMark from "@/components/demo/BrandMark";
import ChatPanel from "@/components/demo/ChatPanel";
import ConsentBanner from "@/components/demo/ConsentBanner";
import {
  ApiError,
  analyzePhoto,
  createSession,
  deleteInspection,
  getHealth,
  sendChat,
  sendConsent,
  uploadPhoto,
} from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

function errorText(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return String(error);
}

export default function DemoJourney() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [connection, setConnection] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inspectionDone, setInspectionDone] = useState(false);
  const [consented, setConsented] = useState<string | null>(null);
  const [consentNote, setConsentNote] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        await getHealth();
        if (!cancelled) setConnection(true);
      } catch {
        if (!cancelled) setConnection(false);
      }
      try {
        const session = await createSession();
        if (!cancelled) setSessionId(session.session_id);
      } catch (e) {
        if (!cancelled) setError(errorText(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleChat = async (text: string) => {
    if (!sessionId || busy) return;
    setBusy(true);
    setError(null);
    setMessages((m) => [...m, { role: "user", content: text }]);
    try {
      const res = await sendChat(sessionId, text);
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `I hit an error: ${errorText(e)}` },
      ]);
    } finally {
      setBusy(false);
    }
  };

  const handlePhoto = async (text: string, file: File) => {
    if (!sessionId || busy) return;
    setBusy(true);
    setError(null);
    setConsentNote(null);
    setConsented(null);
    const message = text || "[Photo attached] — please analyse the damage.";
    setMessages((m) => [
      ...m,
      { role: "user", content: message, preview: URL.createObjectURL(file) },
    ]);
    try {
      await uploadPhoto(sessionId, file);
      const res = await analyzePhoto(sessionId);
      const assistant: ChatMessage = res.status === "OK"
        ? {
            role: "assistant",
            content: res.assistant_message,
            overlay_png_base64: res.overlay_png_base64 ?? undefined,
            quality_status: res.quality_status,
            classes_present: res.classes_present,
            low_confidence: res.low_confidence,
            mean_confidence: res.mean_confidence,
            damage_fraction: res.damage_fraction,
          }
        : {
            role: "assistant",
            content: res.assistant_message,
            quality_status: res.quality_status,
            quality_reasons: res.quality_reasons,
          };
      setMessages((m) => [...m, assistant]);
      setInspectionDone(res.status === "OK");
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `I couldn't analyse that photo: ${errorText(e)}` },
      ]);
    } finally {
      setBusy(false);
    }
  };

  const handleSend = (text: string, photo?: File) => {
    if (photo) {
      void handlePhoto(text, photo);
    } else {
      void handleChat(text);
    }
  };

  const handleConsent = async (granted: boolean) => {
    if (!sessionId || busy) return;
    setBusy(true);
    try {
      const res = await sendConsent(sessionId, granted ? "GRANTED" : "DECLINED");
      setConsented(res.decision);
      setConsentNote(res.note);
      if (res.decision === "DECLINED") {
        setMessages((m) => [
          ...m,
          { role: "assistant", content: "No problem — your photos are only used for this session and will be deleted when it expires." },
        ]);
      }
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  };

  const resetAll = async () => {
    setBusy(true);
    setError(null);
    if (sessionId) {
      try {
        await deleteInspection(sessionId);
      } catch {
        /* best effort — a fresh session is created anyway */
      }
    }
    setSessionId(null);
    setMessages([]);
    setInspectionDone(false);
    setConsented(null);
    setConsentNote(null);
    try {
      const session = await createSession();
      setSessionId(session.session_id);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  };

  const footer = inspectionDone ? (
    <>
      <div className="mt-4 w-full">
        <ConsentBanner
          visible={consented === null}
          busy={busy}
          onChoice={(g) => void handleConsent(g)}
        />
        {consentNote && (
          <p className="mt-2 px-1 text-xs leading-relaxed text-slate-500">{consentNote}</p>
        )}
        {consented === "GRANTED" && (
          <section className="mt-3 rounded-xl border border-emerald-400/20 bg-emerald-400/[0.06] p-4">
            <h3 className="text-sm font-semibold text-emerald-200">Consent saved</h3>
            <p className="mt-1 text-xs leading-relaxed text-slate-300">{consentNote}</p>
          </section>
        )}
      </div>
      <p className="mt-5 px-1 text-center text-[11px] leading-relaxed text-slate-500">
        Demonstration build. Findings are machine predictions with explicit labels
        — never a claim of verified damage extent.
      </p>
    </>
  ) : null;

  const statusLabel = connection === true ? "API online" : connection === false ? "API offline" : "Connecting";
  const statusColor =
    connection === true
      ? "text-emerald-300/90"
      : connection === false
        ? "text-rose-300/90"
        : "text-slate-400";
  const statusDot =
    connection === true ? "bg-emerald-400" : connection === false ? "bg-rose-400" : "bg-slate-500";

  return (
    <div data-shell className="flex h-dvh min-h-dvh flex-col overflow-hidden bg-background text-foreground">
      <header className="relative z-40 flex-none border-b border-white/[0.06] bg-[#0d1218]/85">
        <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4 sm:h-16 sm:px-6">
          <Link
            href="/"
            aria-label="AutoInspect-X home"
            className="group inline-flex items-center gap-2.5 rounded-lg px-1 py-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/60"
          >
            <BrandMark className="h-6 w-6 text-amber-400 transition-transform group-hover:scale-105 sm:h-7 sm:w-7" />
            <span className="text-sm font-semibold tracking-widest text-slate-100 uppercase transition-colors group-hover:text-white">
              AutoInspect<span className="text-amber-400">-X</span>
            </span>
          </Link>
          <div className="flex items-center gap-3 sm:gap-4">
            <span role="status" aria-label={statusLabel} className={`inline-flex items-center gap-1.5 text-xs ${statusColor}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${statusDot}`} aria-hidden />
              {statusLabel}
            </span>
            <button
              type="button"
              onClick={() => void resetAll()}
              disabled={busy}
              className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-sm font-medium text-slate-200 transition hover:border-white/20 hover:bg-white/10 disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/60"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className="h-3.5 w-3.5"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 5v14M5 12h14" />
              </svg>
              New inspection
            </button>
          </div>
        </div>
      </header>

      <ChatPanel
        messages={messages}
        busy={busy}
        onSend={handleSend}
        notice={connection === false ? null : error}
        apiOffline={connection === false}
        footer={footer}
      />
    </div>
  );
}