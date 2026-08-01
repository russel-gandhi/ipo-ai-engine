# Deployment Guide — IPO Insight

Two services: **FastAPI backend** (Render) and **Next.js frontend** (Render or Vercel).

Deploy backend first, then set `NEXT_PUBLIC_API_BASE_URL` on the frontend to the backend URL.

## Quick Deploy (Render Blueprint)

1. Push this repo to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**.
3. Connect the repo — Render reads `render.yaml` at the repo root.
4. Set `NEXT_PUBLIC_API_BASE_URL` on the frontend service to your backend URL (e.g. `https://ipo-insight-backend.onrender.com`).
5. Deploy both services.

## 1. Backend — Render Web Service

| Setting | Value |
|---------|-------|
| **Type** | Web Service |
| **Root directory** | *(repo root)* |
| **Build command** | `pip install -r backend/requirements.txt` |
| **Start command** | `uvicorn backend.src.main:app --host 0.0.0.0 --port $PORT` |
| **Python version** | 3.11+ (`backend/runtime.txt`) |

**Environment variables:**

| Key | Value |
|-----|-------|
| `ENABLE_BACKGROUND_SCRAPER` | `true` (set `false` for faster cold starts on free tier) |

**Free tier note:** Service sleeps after ~15 min idle; first request may take 30–60s. The frontend shows loading skeletons during wake-up.

**Data refresh:** Lazy refresh runs when `/api/live-ipos` is called and cached data is older than 15 minutes. Background scraper also runs every 15 min when enabled.

## 2. Frontend — Vercel (Recommended for Next.js)

1. Import the GitHub repo in [Vercel](https://vercel.com/new).
2. Set **Root Directory** to `frontend`.
3. Add environment variable:
   - `NEXT_PUBLIC_API_BASE_URL` = `https://your-backend.onrender.com`
4. Deploy.

**Local dev:**

```bash
cd frontend
cp .env.example .env.local   # or create .env.local manually
npm install
npm run dev
```

## 2b. Frontend — Render (Alternative)

| Setting | Value |
|---------|-------|
| **Type** | Web Service |
| **Root directory** | `frontend` |
| **Build command** | `npm install && npm run build` |
| **Start command** | `npm start` |
| **Env** | `NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com` |

## 3. CORS

The backend allows all origins (`allow_origins=["*"]`) for demo/judging. For production, restrict to your frontend URL in `backend/src/main.py`.

## 4. Local Development

**Backend:**

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.src.main:app --port 8000 --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — API calls go to http://localhost:8000 by default.

## 5. Pre-deployment Checklist

- [x] Backend runs locally: `uvicorn backend.src.main:app --port 8000`
- [x] Frontend builds: `cd frontend && npm run build`
- [x] No hardcoded localhost in frontend (uses `NEXT_PUBLIC_API_BASE_URL`)
- [ ] Set `NEXT_PUBLIC_API_BASE_URL` on deployed frontend
- [ ] Verify allotment calculator on deployed site
- [ ] Verify verdict card loads for at least one IPO
- [ ] Test cold-start loading state (wait 15–20 min idle, reload)

## 6. Post-deployment Verification

1. Open deployed frontend in incognito.
2. Confirm IPO cards load from `/api/live-ipos`.
3. Open an IPO detail page — allotment calculator and pattern match should populate.
4. Check browser console for CORS or fetch errors.

## 7. README Live URL Placeholder

After deploying, add your live URLs to the root `README.md`:

```markdown
## Live Demo
- **Frontend:** https://your-app.vercel.app
- **Backend API:** https://your-backend.onrender.com
- *Note: Backend may take up to 60s to wake on first load (Render free tier).*
```
