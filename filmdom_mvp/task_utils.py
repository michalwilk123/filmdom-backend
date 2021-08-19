from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ["TMDB_API_KEY"]


def create_raw_movie_query() -> str:
    date = datetime.now() - timedelta(days=1)
    date_str = date.strftime("%m_%d_%Y")
    return f"http://files.tmdb.org/p/exports/movie_ids_{date_str}.json.gz"


def create_movie_query(movie_id: int) -> str:
    return f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"


def create_genres_query() -> str:
    return f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=en-US"


def create_valid_thumbnail_url(src: str):
    return f"https://image.tmdb.org/t/p/original/{src}"
