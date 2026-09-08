/// Canvas sizing and object-cover composition math shared by the cinematic
/// renderer. Kept small and pure so the component stays focused.
type Size = { width: number; height: number };

/**
 * Compute a draw rect (in CSS px) that covers `viewport` with `src`,
 * then scale it to the backing canvas via `scaleX/scaleY`. Mirrors
 * CSS `object-fit: cover`.
 */
export function coverRect(
  src: Size,
  viewport: Size,
  scaleX: number,
  scaleY: number,
): { dx: number; dy: number; dw: number; dh: number } {
  const target = viewport.width / viewport.height;
  const source = src.width / src.height;
  let dw: number;
  let dh: number;
  if (source > target) {
    // Source is wider -> scale by height, crop the sides.
    dh = viewport.height;
    dw = dh * source;
  } else {
    // Source is taller -> scale by width, crop top/bottom.
    dw = viewport.width;
    dh = dw / source;
  }
  return {
    dx: (viewport.width - dw) / 2,
    dy: (viewport.height - dh) / 2,
    dw: dw * scaleX,
    dh: dh * scaleY,
  };
}
