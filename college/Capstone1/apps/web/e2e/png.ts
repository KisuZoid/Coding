/**
 * Self-contained synthetic-image fixtures for the browser E2E suite.
 *
 * We synthesise real PNGs in Node (zlib) instead of shipping binary assets or
 * depending on Python at test time. The pixel math mirrors the backend E2E
 * fixtures (tests/test_e2e_integration.py) that are already validated against
 * ImageQualityValidator: a checkerboard + dark patch passes every capture
 * check, and a heavily box-blurred copy fails as TOO_BLURRY.
 */

import { deflateSync } from "node:zlib";

const CRC_TABLE = new Int32Array(256).map((_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c;
});

function crc32(buf: Uint8Array): number {
  let c = -1;
  for (const byte of buf) c = CRC_TABLE[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ -1) >>> 0;
}

function chunk(type: string, data: Uint8Array): Buffer {
  const typeBuf = Buffer.from(type, "ascii");
  const out = Buffer.alloc(8 + data.length + 4);
  out.writeUInt32BE(data.length, 0);
  typeBuf.copy(out, 4);
  Buffer.from(data).copy(out, 8);
  out.writeUInt32BE(crc32(Buffer.concat([typeBuf, Buffer.from(data)])), 8 + data.length);
  return out;
}

/** Encode an RGB image as a PNG (color type 2, bit depth 8, filter 0 rows). */
export function rgbPng(width: number, height: number, pixel: (x: number, y: number) => [number, number, number]): Buffer {
  const raw = Buffer.alloc(height * (1 + width * 3));
  let off = 0;
  for (let y = 0; y < height; y++) {
    raw[off++] = 0;
    for (let x = 0; x < width; x++) {
      const [r, g, b] = pixel(x, y);
      raw[off++] = r;
      raw[off++] = g;
      raw[off++] = b;
    }
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 2; // color type: truecolor
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk("IHDR", ihdr),
    chunk("IDAT", deflateSync(raw)),
    chunk("IEND", new Uint8Array()),
  ]);
}

/** Deterministic, seedable integer noise in [-8, 8] (mulberry32). */
function noise(seed: number, x: number, y: number): number {
  let t = seed + x * 374761393 + y * 668265263;
  t = (t ^ (t >>> 13)) >>> 0;
  t = Math.imul(t, 1274126177) >>> 0;
  t = t ^ (t >>> 16);
  return -8 + Math.floor((t / 4294967296) * 17);
}

function checkerValue(x: number, y: number): number {
  const base = Math.floor((x + y) / 16) % 2 === 0 ? 156 : 100;
  const v = Math.max(0, Math.min(255, base + noise(0, x, y)));
  if (x >= 96 && x < 160 && y >= 96 && y < 160) return 40;
  return v;
}

function boxBlur(width: number, height: number, src: Uint8Array, radius: number, passes: number): Uint8Array {
  let cur = src;
  const size = width * height;
  for (let pass = 0; pass < passes; pass++) {
    const next = new Uint8Array(size);
    const w = radius * 2 + 1;
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        let sum = 0;
        for (let dy = -radius; dy <= radius; dy++) {
          const yy = Math.min(height - 1, Math.max(0, y + dy));
          for (let dx = -radius; dx <= radius; dx++) {
            sum += cur[yy * width + Math.min(width - 1, Math.max(0, x + dx))];
          }
        }
        next[y * width + x] = Math.round(sum / (w * w));
      }
    }
    cur = next;
  }
  return cur;
}

const SIZE = 256;

/** Sharp checkerboard + dark patch: passes all capture-quality checks. */
export function validImage(): Buffer {
  const gray = new Uint8Array(SIZE * SIZE);
  for (let y = 0; y < SIZE; y++) {
    for (let x = 0; x < SIZE; x++) gray[y * SIZE + x] = checkerValue(x, y);
  }
  return rgbPng(SIZE, SIZE, (x, y) => {
    const v = gray[y * SIZE + x];
    return [v, v, v];
  });
}

/** Heavily blurred copy of validImage(): fails as TOO_BLURRY. */
export function blurryImage(): Buffer {
  const gray = new Uint8Array(SIZE * SIZE);
  for (let y = 0; y < SIZE; y++) {
    for (let x = 0; x < SIZE; x++) gray[y * SIZE + x] = checkerValue(x, y);
  }
  const blurred = boxBlur(SIZE, SIZE, gray, 3, 14);
  return rgbPng(SIZE, SIZE, (x, y) => {
    const v = blurred[y * SIZE + x];
    return [v, v, v];
  });
}