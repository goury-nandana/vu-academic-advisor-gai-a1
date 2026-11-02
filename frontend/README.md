# VU Academic Advisor — Next.js frontend

Design: white chat UI with one campus photo background, collapsible frosted side panel, fixed header pill
(green ring while the advisor is answering, fades 5 s after the reply), and one bottom bar (mic, camera, file, send).

## Run locally
```bash
npm install
npm run dev
```

## Deploy (Vercel)
Import the repo, set **Root Directory** to `frontend`.

## Connecting the advisor backend
All backend access is in `app/advisor.ts`. Set `NEXT_PUBLIC_ADVISOR_API_URL` (a public URL only; keep Groq keys on the server)
in Vercel → Project → Settings → Environment Variables. Without it the page shows a "not connected" reply.

Expected API: `POST {URL}/chat` (multipart/form-data) with `question`, `history` (JSON), `profile` (JSON), `files[]`,
returning JSON `{ "answer": string, "sources": [{ "title": string, "url"?: string }] }`.
