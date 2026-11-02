# VU Academic Advisor — Next.js frontend

This is the Vercel-oriented frontend workspace. Import the repository into Vercel and set **Root Directory** to `frontend`.

## Local preview

```bash
npm install
npm run dev
```

## Current status

The responsive UI is scaffolded with a preview-only chat response. The academic service has not been connected yet; do not treat preview responses as academic guidance. Existing Streamlit app remains the live, functional application until API integration is complete.

Groq credentials belong only on the server/backend and must never be added to browser-exposed `NEXT_PUBLIC_*` variables.