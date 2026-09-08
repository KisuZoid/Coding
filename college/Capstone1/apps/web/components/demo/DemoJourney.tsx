"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import ChatPanel from "@/components/demo/ChatPanel";
import ConsentBanner from "@/components/demo/ConsentBanner";
import ContextCard from "@/components/demo/ContextCard";
import PhotoBay from "@/components/demo/PhotoBay";
import ResultBlocks from "@/components/demo/ResultBlocks";
import { ApiError, analyzePhoto, createSession, deleteInspection, getHealth, getInspection, sendChat, uploadPhoto } from "@/lib/api";
import type { ChatMessage, ChatResponse, InspectionStateView } from "@/lib/types";

type PhotoPhase = "ask" | "upload" | "analysing" | "retake" | "done";

function errorText(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return String(error);
}

interface QualityReject {
  status: string;
  reasons?: string[];
}

const QUALITY_REJECT_COPY: Record<string, string> = {
  TOO_BLURRY: "Your photo looks blurry. Hold the phone steady and retake close up.",
  TOO_DARK: "Your photo is too dark. Retake it in brighter light.",
  EXCESSIVE_GLARE: "There's too much glare. Angle the phone away from the light source.",
  INSUFFICIENT_CONTEXT:
    "Your photo is too flat and low-contrast. Make sure the damaged area fills the frame.",
};

export default function DemoJourney() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [waitingFor, setWaitingFor] = useState<string | null>(null);
  const [finished, setFinished] = useState(false);
  const [insp, setInsp] = useState<InspectionStateView | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connection, setConnection] = useState<boolean | null>(null);
  const [photoPhase, setPhotoPhase] = useState<PhotoPhase>("ask");
  const [photoRejected, setPhotoRejected] = useState<string | null>(null);

  async function fetchInspection(id: string) {
    const { state } = await getInspection(id);
    setInsp(state);
  }

  async function runTurn(text: string): Promise<ChatResponse | null> {
    if (!sessionId || busy) return null;
    setBusy(true);
    setError(null);
    setMessages((m) => [...m, { role: "user", content: text }]);
    try {
      const res = await sendChat(sessionId, text);
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
      setWaitingFor(res.waiting_for);
      setFinished(res.finished);
      await fetchInspection(sessionId);
      return res;
    } catch (e) {
      setError(errorText(e));
      return null;
    } finally {
      setBusy(false);
    }
  }

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
        if (cancelled) return;
        setSessionId(session.session_id);
        await fetchInspection(session.session_id);
      } catch (e) {
        if (!cancelled) setError(errorText(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handlePhoto = async (file: File) => {
    if (!sessionId || busy) return;
    setError(null);
    setPhotoRejected(null);
    setPhotoPhase("upload");
    try {
      await uploadPhoto(sessionId, file);
      await analyzePhoto(sessionId);
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) {
        const detail = ((e.body as { detail?: unknown })?.detail ??
          e.body) as QualityReject | null;
        const reason =
          QUALITY_REJECT_COPY[detail?.status ?? ""] ??
          (detail?.reasons?.[0] ?? "The photo quality was rejected. Please retake it.");
        setPhotoRejected(reason);
        setPhotoPhase("retake");
        return;
      }
      setError(errorText(e));
      setPhotoPhase("ask");
      return;
    }
    setPhotoPhase("analysing");
    const res = await runTurn("Photo uploaded — what do you think?");
    setPhotoPhase(res?.waiting_for === "PHOTO" ? "retake" : "done");
  };

  const handleConsent = async (granted: boolean) => {
    await runTurn(granted ? "yes" : "no");
  };

  const handleFinish = async () => {
    await runTurn("I am done, please wrap up.");
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
    setWaitingFor(null);
    setFinished(false);
    setInsp(null);
    setPhotoPhase("ask");
    setPhotoRejected(null);
    try {
      const session = await createSession();
      setSessionId(session.session_id);
      await fetchInspection(session.session_id);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  };

  const hasImage = Boolean(insp?.image_asset_id);
  const analysing = busy && Boolean(insp?.analysis) && !insp?.repair && !insp?.cost;

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b border-slate-800 bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
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
              onClick={resetAll}
              disabled={busy}
              className="text-xs font-medium text-slate-400 transition hover:text-slate-100 disabled:opacity-40"
            >
              New inspection
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-8">
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

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
          <div className="order-2 h-[560px] lg:order-1 lg:sticky lg:top-20 lg:h-[calc(100vh-7rem)]">
            <ChatPanel
              messages={messages}
              busy={busy}
              disabled={finished}
              onSend={(t) => void runTurn(t)}
            />
          </div>

          <div className="order-1 space-y-5 lg:order-2">
            <ContextCard insp={insp} />

            <PhotoBay
              waitingFor={waitingFor}
              hasImage={hasImage}
              busy={busy}
              phase={photoPhase}
              rejectReason={photoRejected}
              onFile={(f) => void handlePhoto(f)}
            />

            <ConsentBanner waitingFor={waitingFor} busy={busy} onChoice={(g) => void handleConsent(g)} />

            {waitingFor === "FINISH" && !finished && (
              <button
                type="button"
                disabled={busy}
                onClick={() => void handleFinish()}
                className="w-full rounded-xl border border-slate-600 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:bg-slate-800 disabled:opacity-40"
              >
                {busy ? "Working..." : "Finish and show summary"}
              </button>
            )}

            <ResultBlocks insp={insp} analysing={analysing} />

            {finished && (
              <section className="rounded-2xl border border-emerald-400/40 bg-emerald-400/10 p-5">
                <h3 className="text-sm font-semibold text-emerald-200">Inspection complete</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-300">
                  Your photos are kept only for this session and are deleted when
                  it expires. Thanks for using AutoInspect-X.
                </p>
                <Link
                  href="/"
                  className="mt-4 inline-block text-sm font-medium text-amber-300 hover:text-amber-200"
                >
                  Back to the intro
                </Link>
              </section>
            )}

            {!finished && (
              <p className="px-1 pb-6 text-center text-[11px] leading-relaxed text-slate-500">
                Demonstration build. Model findings, repair suggestions and cost are
                machine predictions with explicit labels — never a real quote.
              </p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}