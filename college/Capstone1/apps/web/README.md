# AutoInspect-X — web frontend

Next.js (App Router) + React 19 + TypeScript (strict) + Tailwind UI for the
AutoInspect-X demo. Runs the phases L–O experience: scroll-driven cinematic
intro (`/`), then the single inspection journey (`/demo`) — agent chat, photo
guidance/upload/validation, result blocks with overlay, optional training
consent, and completion.

## Run

```bash
# 1. Backend (ai conda env, port 8000)
source ~/miniconda3/etc/profile.d/conda.sh && conda activate ai
uvicorn apps.api.main:app --reload

# 2. Frontend
cd apps/web && npm install && npm run dev
```

Open http://localhost:3000.

The browser talks to the API via `NEXT_PUBLIC_API_URL` (default
`http://localhost:8000`). Backend CORS is limited to the origins in
`CORS_ORIGINS` (default `["http://localhost:3000"]`).

The cinematic intro serves the four clips through a symlink:
`apps/web/public/videos -> repo-root/public` (the clips live at repo root).

## Quality gates

```bash
npm run lint      # eslint
npm run typecheck # tsc --noEmit
npm run build     # next build (type check + lint + build)
```