from datetime import datetime, timedelta

API_KEY = "4d571ebf7300e30c04862d92ad6d4936"


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
