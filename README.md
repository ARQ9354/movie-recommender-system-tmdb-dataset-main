# Movie Recommender System (TMDB)

A content-based movie recommender built on the TMDB 5000 dataset. The UI is a
fast, modern FastAPI + Tailwind CSS frontend; the ML logic (pickle artifacts)
is unchanged.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000

## Deploy to Render

1. Push this repo to GitHub (pickle files are stored with Git LFS).
2. In Render, create a new **Web Service** and connect the repo (or use the
   included `render.yaml` as a Blueprint).
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. (Optional) Set `TMDB_API_KEY` env var for poster fetching.

The included `render.yaml` / `Procfile` already encode these settings.
