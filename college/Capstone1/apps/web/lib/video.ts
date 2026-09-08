/// Cinematic timeline data. The four clips run back-to-back on one 30.42 s
/// timeline and are driven by scroll progress (scrollY -> currentTime).
///
/// NARRATIVE COPY: deliberately neutral — this repository's coding agent
/// cannot see the clips, so no copy that presumes unseen visual content may be
/// hard-coded. Replace the `copy` strings once a vision-capable reviewer (or
/// the author) confirms what each segment actually shows.

export interface Clip {
  src: string;
  start: number;
  end: number;
  tone: "bright" | "muted" | "warm" | "contrast";
}

export interface CinematicSegment {
  title: string;
  body: string;
  eyebrow: string;
}

export const TOTAL_SECONDS = 30.42;

export const CLIPS: Clip[] = [
  { src: "/videos/1.mp4", start: 0, end: 10.0, tone: "bright" },
  { src: "/videos/2.mp4", start: 10.0, end: 18.0, tone: "muted" },
  { src: "/videos/3.mp4", start: 18.0, end: 22.42, tone: "warm" },
  { src: "/videos/4.mp4", start: 22.42, end: 30.42, tone: "contrast" },
];

export const SEGMENTS: CinematicSegment[] = [
  {
    eyebrow: "01 — Meet AutoInspect-X",
    title: "An AI-assisted damage inspection, start to finish.",
    body: "Upload a photo, chat in plain words, and get a clearly honest reading of what's found.",
  },
  {
    eyebrow: "02 — Tell us what happened",
    title: "Describe the incident in plain words.",
    body: "The conversational agent builds the inspection context from what you say — no complex forms.",
  },
  {
    eyebrow: "03 — Share a photo",
    title: "Upload a clear picture of the damage.",
    body: "A photo guidance + validation loop checks the shot before any analysis begins.",
  },
  {
    eyebrow: "04 — A clear, honest result",
    title: "We show what we found — and what we can't know.",
    body: "Model findings, estimates, and limits are always labelled. Low-confidence results say so.",
  },
];

/** Map 0..1 scroll progress to a { clipIndex, seconds } frame on the timeline. */
export function frameFor(progress: number): { clipIndex: number; seconds: number } {
  const t = Math.min(1, Math.max(0, progress)) * TOTAL_SECONDS;
  for (let i = 0; i < CLIPS.length; i += 1) {
    const clip = CLIPS[i];
    if (t < clip.end) {
      return { clipIndex: i, seconds: t - clip.start };
    }
  }
  const last = CLIPS.length - 1;
  return { clipIndex: last, seconds: CLIPS[last].end - CLIPS[last].start };
}