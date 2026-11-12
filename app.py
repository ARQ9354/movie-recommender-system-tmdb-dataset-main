import os
import pickle
import requests
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load the model artifacts once at startup.
movie_file_path = os.path.join(BASE_DIR, "movie_list.pkl")
similarity_file_path = os.path.join(BASE_DIR, "similarity.pkl")

movies = pickle.load(open(movie_file_path, "rb"))
similarity = pickle.load(open(similarity_file_path, "rb"))

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "8265bd1679663a7ea12ac168da84d2e8")
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500/"


def fetch_poster(movie_id):
    """Fetch a movie poster URL from TMDB, with a safe fallback."""
    try:
        url = (
            "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(
                movie_id, TMDB_API_KEY
            )
        )
        data = requests.get(url, timeout=8).json()
        poster_path = data.get("poster_path")
        if poster_path:
            return TMDB_IMAGE_BASE + poster_path
    except Exception:
        pass
    return "https://via.placeholder.com/500x750/1f2937/9ca3af?text=No+Poster"


def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    selected = [(movies.iloc[i[0]].movie_id, movies.iloc[i[0]].title) for i in distances[1:6]]

    recommended_movie_names = [title for _, title in selected]
    with ThreadPoolExecutor(max_workers=5) as executor:
        recommended_movie_posters = list(executor.map(lambda x: fetch_poster(x[0]), selected))
    return recommended_movie_names, recommended_movie_posters


app = FastAPI(title="Movie Recommender System")

templates_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/movies")
async def api_movies():
    return {"movies": movies["title"].tolist()}


@app.get("/api/recommend")
async def api_recommend(movie: str):
    if movie not in set(movies["title"].tolist()):
        raise HTTPException(status_code=404, detail="Movie not found")
    names, posters = recommend(movie)
    return {"names": names, "posters": posters}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request, "movies": movies["title"].tolist()},
    )
