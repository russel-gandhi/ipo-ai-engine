# Deployment Guide — Render

Two services on Render: the FastAPI backend and the React frontend. Deploy
backend first so you have a live URL to point the frontend at.

## 1. Backend — Render Web Service

- **Type:** Web Service (not Static Site — it needs to run a Python process)
- **Root directory:** `backend/`
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
  (Render injects `$PORT` — do not hardcode a port number)
- **Environment:** Python 3.11+ (set in Render's environment settings or via
  a `runtime.txt` file in `backend/`)
- **Free tier note:** the service sleeps after ~15 min of inactivity and
  takes 30-60s to wake on the next request. This is fine for a demo/judging
  context — just make sure the frontend shows a loading state instead of
  looking broken during cold start (see AGENT_RULES.md §6). If you want to
  avoid cold starts entirely for the judging window specifically, a paid
  tier removes this, but the free tier is fine if the frontend handles it
  gracefully.
- **Scraper/refresh job:** since Render web services don't run persistent
  background cron jobs on the free tier by default, implement the refresh
  as: (a) triggered on-demand when an API endpoint is called and the cached
  data is older than the refresh interval ("lazy refresh"), which is simpler
  and works fine on free tier, OR (b) a separate Render Cron Job service if
  time allows for a cleaner "always fresh" feel. Start with (a) — it's less
  infrastructure and is honestly a better fit for the "last updated X min
  ago" UI pattern already planned.

## 2. Frontend — Render Static Site

- **Type:** Static Site
- **Root directory:** `frontend/`
- **Build command:** `npm install && npm run build`
- **Publish directory:** `dist` (Vite's default build output folder)
- **Environment variable:** set `VITE_API_BASE_URL` to the deployed
  backend's Render URL (e.g. `https://ipo-insight-backend.onrender.com`) —
  reference this in `frontend/src/api/client.ts` instead of hardcoding
  localhost, so the same code works in dev and production

## 3. CORS
The FastAPI backend must explicitly allow the frontend's Render URL as an
origin, or every request from the deployed frontend will fail silently with
a CORS error that's confusing to debug. In `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # local dev
        "https://<your-frontend-service-name>.onrender.com",  # deployed
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Set this up EARLY (Stage 4, not Stage 10) and test it against a real deployed
frontend once both services are up — don't leave CORS as a deployment-day
surprise.

## 4. Pre-deployment checklist
- [ ] Backend runs locally with `uvicorn main:app` and responds correctly
- [ ] Frontend build (`npm run build`) completes without errors locally
      before pushing — Render will fail the deploy on the same errors,
      better to catch them locally first
- [ ] No hardcoded `localhost` URLs anywhere in frontend code
- [ ] `.env` / secrets are NOT committed to the public GitHub repo — use
      Render's environment variable settings instead
- [ ] CORS configured with the actual deployed frontend URL, not just
      localhost

## 5. Post-deployment verification
Per AGENT_RULES.md §6, don't consider the project done until this is
checked:
- [ ] Open the deployed frontend URL in an incognito window (not just your
      own browser with cached local state)
- [ ] Confirm the allotment calculator returns a real computed result
- [ ] Confirm the verdict card shows real data for at least one tracked IPO
      (Indo-MIM)
- [ ] Let the backend go idle (wait ~15-20 min) then hit the live frontend
      again to confirm the cold-start loading state works and doesn't error
      out or hang indefinitely
- [ ] Check the browser console for any CORS or failed-fetch errors

## 6. What to put in the README
- The live Render URL, prominently, near the top
- A one-line note that the backend may take up to a minute to wake up on
  first load (free tier) — set the expectation instead of letting a judge
  think it's broken
