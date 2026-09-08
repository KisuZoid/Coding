/// Cinematic image-sequence timeline.
///
/// The four scenes are treated as ONE continuous scroll-driven sequence.
/// Each scene is a folder of 30 FPS JPEG frames named `ezgif-frame-NNN.jpg`
/// (frames 001..N, zero-padded to 3 digits). The source frames are served
/// from `/videos/{1..4}/...` via the `public/videos -> ../../../public`
/// symlink.
///
/// Geometry per scene was measured from the actual files (see frame audit):
///   Scene 1: 300 x 1920x1080  (16:9)
///   Scene 2: 240 x 1920x1080  (16:9)
///   Scene 3: 133 x 1280x720   (16:9)
///   Scene 4: 240 x 1920x1080  (16:9)
///
/// Total = 913 frames.

export interface SceneText {
  eyebrow: string;
  title: string;
  body: string;
}

export interface CinematicScene {
  id: number;
  folder: "1" | "2" | "3" | "4";
  frameCount: number;
  width: number;
  height: number;
  /** First and last global frame index (inclusive) for this scene. */
  startFrame: number;
  endFrame: number;
  /** 0..1 section progress where this scene's headline appears/fades. */
  textStart: number;
  textEnd: number;
  text: SceneText;
}

const SCENE_DEFS: Omit<CinematicScene, "startFrame" | "endFrame">[] = [
  {
    id: 1,
    folder: "1",
    frameCount: 300,
    width: 1920,
    height: 1080,
    // text covers roughly the first half of the scene
    textStart: 0.05,
    textEnd: 0.55,
    text: {
      eyebrow: "01 — AutoInspect-X",
      title: "An AI-assisted damage inspection, start to finish.",
      body: "Photo in, honest reading out — damage analysis with clearly labelled confidence.",
    },
  },
  {
    id: 2,
    folder: "2",
    frameCount: 240,
    width: 1920,
    height: 1080,
    textStart: 0.1,
    textEnd: 0.65,
    text: {
      eyebrow: "02 — Tell us what happened",
      title: "Describe the incident in plain words.",
      body: "The conversational agent builds context from what you say — no complex forms.",
    },
  },
  {
    id: 3,
    folder: "3",
    frameCount: 133,
    width: 1280,
    height: 720,
    textStart: 0.05,
    textEnd: 0.8,
    text: {
      eyebrow: "03 — Share a photo",
      title: "Upload a clear picture of the damage.",
      body: "Photo guidance and validation check the shot before any analysis begins.",
    },
  },
  {
    id: 4,
    folder: "4",
    frameCount: 240,
    width: 1920,
    height: 1080,
    textStart: 0.1,
    textEnd: 0.7,
    text: {
      eyebrow: "04 — The result",
      title: "We show what we found — and what we can't know.",
      body: "Model findings, estimates, and limits are always labelled. Low confidence says so.",
    },
  },
];

function pad(n: number): string {
  return String(n).padStart(3, "0");
}

export function sceneUrl(scene: number, frame: number): string {
  return `/videos/${scene}/ezgif-frame-${pad(frame)}.jpg`;
}

/** Total number of frames across all scenes. */
export const TOTAL_FRAMES = SCENE_DEFS.reduce((acc, s) => acc + s.frameCount, 0);

/** Global frame ranges assigned to each scene, weighted by frame count. */
export const SCENES: CinematicScene[] = (() => {
  let cursor = 0;
  return SCENE_DEFS.map((s) => {
    const start = cursor;
    cursor += s.frameCount;
    return { ...s, startFrame: start, endFrame: cursor - 1 };
  });
})();

export interface FramePosition {
  scene: CinematicScene;
  /** 1-based frame number within the scene folder. */
  localFrame: number;
  /** frame path on disk */
  src: string;
}

/**
 * Map a smoothly interpolated 0..1 progress value to a concrete frame.
 * Deterministic: uses normalized section progress, NOT scrollY % frameCount.
 */
export function frameForProgress(progress: number): FramePosition {
  const p = Math.min(1, Math.max(0, progress));
  const global = Math.round(p * (TOTAL_FRAMES - 1));
  for (const scene of SCENES) {
    if (global >= scene.startFrame && global <= scene.endFrame) {
      return {
        scene,
        localFrame: global - scene.startFrame + 1,
        src: sceneUrl(scene.id, global - scene.startFrame + 1),
      };
    }
  }
  const last = SCENES[SCENES.length - 1];
  return { scene: last, localFrame: last.frameCount, src: sceneUrl(last.id, last.frameCount) };
}

/** Index (0-based) of the scene whose text should be shown at `progress`. */
export function segmentAt(progress: number): number {
  const p = Math.min(1, Math.max(0, progress));
  const global = p * (TOTAL_FRAMES - 1);
  for (let i = 0; i < SCENES.length; i += 1) {
    const s = SCENES[i];
    if (global >= s.startFrame && global <= s.endFrame) return i;
  }
  return SCENES.length - 1;
}
