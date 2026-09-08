"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { CLIPS, SEGMENTS, TOTAL_SECONDS, frameFor } from "@/lib/video";

/**
 * Scroll-driven cinematic intro (Phase O).
 *
 * One ~300vh section pins a full-screen stage; scroll progress is mapped onto a
 * single 30.42 s timeline and each clip's <video>.currentTime is seeked to the
 * matching frame. Videos alternate by crossfade, and the narrative copy overlays
 * fade per segment. With prefers-reduced-motion the auto-seek is disabled and
 * the clips simply sit at their first frame (copy still advances by segment).
 *
 * Narrative copy lives in lib/video.ts. It is deliberately neutral pending
 * visual confirmation of clip content.
 */
export default function CinematicIntro() {
  const holderRef = useRef<HTMLDivElement>(null);
  const videoRefs = useRef<Array<HTMLVideoElement | null>>([]);
  const rafRef = useRef(0);
  const [progress, setProgress] = useState(0);
  const [segment, setSegment] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = requestAnimationFrame(() => {
        const el = holderRef.current;
        if (!el) return;
        const travel = el.scrollHeight || el.getBoundingClientRect().height;
        const span = travel - window.innerHeight;
        if (span <= 0) return;
        const rect = el.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, -rect.top / span));
        setProgress(p);
        setSegment(frameFor(p).clipIndex);
      });
    };

    const onLoaded = () => onScroll();

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onLoaded);
    onLoaded();
    return () => {
      cancelAnimationFrame(rafRef.current);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onLoaded);
    };
  }, []);

  useEffect(() => {
    let reduceMotion = false;
    try {
      reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch {
      reduceMotion = false;
    }
    if (reduceMotion) return;

    const { clipIndex, seconds } = frameFor(progress);
    videoRefs.current.forEach((video, i) => {
      if (!video) return;
      if (i === clipIndex) {
        video.pause();
        try {
          if (Math.abs(video.currentTime - seconds) > 0.3) video.currentTime = seconds;
        } catch {
          /* media not ready — retry on next frame */
        }
      } else {
        video.pause();
      }
    });
  }, [progress]);

  const active = SEGMENTS[segment];
  const atEnd = progress > 0.92;

  return (
    <div ref={holderRef} className="relative h-[320vh] cinematic-scroll">
      <div className="sticky top-0 h-screen w-full overflow-hidden bg-black">
        {/* Video stage */}
        {CLIPS.map((clip, i) => (
          <video
            key={clip.src}
            ref={(el) => {
              videoRefs.current[i] = el;
            }}
            src={clip.src}
            className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-500 ${
              i === segment ? "opacity-100" : "opacity-0"
            }`}
            muted
            playsInline
            preload="metadata"
            loop
            aria-hidden
          />
        ))}
        <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/25 to-black/85" />

        {/* Narrative overlay */}
        <div
          key={segment}
          className="absolute inset-x-0 bottom-24 space-y-4 px-6 text-center text-white sm:bottom-28 sm:px-12"
        >
          <p className="animate-[pulse-soft_1.2s_ease-in-out] text-xs font-semibold tracking-[0.3em] text-amber-300/90 uppercase sm:text-sm">
            {active.eyebrow}
          </p>
          <h2 className="mx-auto max-w-3xl text-3xl font-semibold leading-tight text-white sm:text-5xl">
            {active.title}
          </h2>
          <p className="mx-auto max-w-xl text-sm leading-relaxed text-slate-200/90 sm:text-base">
            {active.body}
          </p>
        </div>

        {/* Progress */}
        <div className="absolute inset-x-0 bottom-0 h-1 bg-white/10">
          <div
            className="h-full bg-amber-400 transition-[width] duration-150 ease-linear"
            style={{ width: `${progress * 100}%` }}
          />
        </div>

        {/* Timeline ruler */}
        <div className="absolute right-6 top-1/2 hidden -translate-y-1/2 flex-col items-center gap-3 sm:flex">
          {SEGMENTS.map((_, i) => (
            <span
              key={i}
              className={`h-2 w-2 rounded-full ${
                i <= segment ? "bg-amber-400" : "bg-white/30"
              }`}
            />
          ))}
        </div>

        {/* Scroll hint */}
        {!atEnd && (
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 text-[11px] tracking-widest text-white/60 uppercase">
            Scroll
          </div>
        )}

        {/* Call to action */}
        <div
          className={`absolute inset-0 flex items-center justify-center transition-opacity duration-700 ${
            atEnd ? "opacity-100" : "pointer-events-none opacity-0"
          }`}
        >
          <Link
            href="/demo"
            className="rounded-full bg-amber-400 px-8 py-4 text-base font-semibold text-black shadow-lg shadow-amber-400/30 transition hover:bg-amber-300"
          >
            Start an inspection
          </Link>
        </div>

        <p className="absolute right-4 bottom-6 hidden text-[10px] tracking-widest text-white/40 uppercase sm:block">
          {String(Math.round(progress * TOTAL_SECONDS * 10) / 10).padStart(4, " ")} s /{" "}
          {TOTAL_SECONDS.toFixed(1)} s
        </p>
      </div>
    </div>
  );
}