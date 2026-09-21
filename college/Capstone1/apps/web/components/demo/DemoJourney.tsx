"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

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
          }
        : { role: "assistant", content: res.assistant_message, quality_status: res.quality_status };
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

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b border-slate-800 bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-5 py-4">
          <span className="text-sm font-semibold tracking-widest uppercase text-slate-100">
            AutoInspect<span className="text-amber-400">-X</span>
          </span>
          <div className="flex items-center gap-4">
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${
                connection === true
                  ? "bg-emerald-500/10 text-emerald-300"
                  : connection === false
                    ? "bg-rose-500/10 text-rose-300"
                    : "bg-slate-800 text-slate-400"
              }`}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-current" />
              {connection === true ? "API online" : connection === false ? "API offline" : "Connecting"}
            </span>
            <button
              type="button"
              onClick={() => void resetAll()}
              disabled={busy}
              className="text-xs font-medium text-slate-400 transition hover:text-slate-100 disabled:opacity-40"
            >
              New inspection
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-5 py-8">
        {connection === false && (
          <div className="mb-6 rounded-2xl border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-200">
            The AutoInspect-X API is not reachable. Start the backend
            (uvicorn apps.api.main:app in the ai conda environment) and reload this page.
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-2xl border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-200">
            {error}
          </div>
        )}

        <div className="h-[62vh] min-h-[480px]">
          <ChatPanel messages={messages} busy={busy} onSend={handleSend} />
        </div>

        {inspectionDone && (
          <div className="mt-5 space-y-4">
            <ConsentBanner
              visible={consented === null}
              busy={busy}
              onChoice={(g) => void handleConsent(g)}
            />
            {consentNote && (
              <p className="px-1 text-xs leading-relaxed text-slate-500">{consentNote}</p>
            )}
            {consented === "GRANTED" && (
              <section className="rounded-2xl border border-emerald-400/40 bg-emerald-400/10 p-5">
                <h3 className="text-sm font-semibold text-emerald-200">Consent saved</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-300">
                  {consentNote}
                </p>
              </section>
            )}
            <p className="px-1 pb-6 text-center text-[11px] leading-relaxed text-slate-500">
              Demonstration build. Findings are machine predictions with explicit
              labels — never a claim of verified damage extent.
            </p>
            <Link
              href="/"
              className="mt-2 inline-block text-center text-sm font-medium text-amber-300 hover:text-amber-200"
            >
              Back to the intro
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}