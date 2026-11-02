# VU Academic Advisor — Next.js frontend

The frontend talks to the FastAPI academic advisor using the same Vercel origin at `/api/chat`.

## Run frontend locally
```bash
npm install
npm run dev
```

For local API-backed testing, run the FastAPI service from `backend/` separately and configure a local Next.js rewrite or use the Vercel Services local development workflow.

## Deploy to Vercel
Import the repository with its **Root Directory set to the repository root**, not `frontend`. The repository-level `vercel.json` defines the frontend and backend Vercel Services and routes `/api/*` to FastAPI.

Set `GROQ_API_KEY` as a private environment variable on the backend service in Vercel. Do not expose it to the browser or use a `NEXT_PUBLIC_` variable.

## API contract
POST `/api/chat` as multipart/form-data:
- `question`: text
- `history`: JSON array of prior user/assistant turns
- `profile`: JSON object of explicitly provided student details
- `files`: optional attachments (PDF, DOCX, TXT, MD, CSV, XLSX, PPTX; up to 15 MB each; text extraction only)

Returns JSON `{ "answer": string, "sources": [{ "title": string, "url"?: string }] }`.
