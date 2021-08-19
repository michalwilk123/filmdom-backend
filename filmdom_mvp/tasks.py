from celery.app import utils
from filmdom.celery import app
import logging
from datetime import datetime
import aiohttp
import gzip
import asyncio
import json
import logging
from . import task_utils
from celery.signals import worker_ready
from celery.schedules import crontab
from . import models
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("filmdom_worker.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
)
logger.addHandler(file_handler)


@app.on_after_finalize.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=7, minute=0),
        fetch_movie_data.s(),
        name="fetch movie data",
    )


@worker_ready.connect
def at_start(sender, **kwargs):
    logger.info("The celery movie fetching task has started")


@app.task
def fetch_movie_data():
    logger.debug("Started task: fetching movie data from TMDM API")
    asyncio.run(start_data_fetch())
    logger.debug("TMDB Celery task has finished with success")


def decompress_request(data: bytes) -> str:
    logger.debug("Decompressing recieved data")
    return gzip.decompress(data).decode("utf-8")


def request_to_python_obj(data: str) -> list:
    logger.debug("Parsing raw string data into python object")
    data = "[" + data.replace("\n", ",")[:-1] + "]"
    return json.loads(data)


async def check_if_movie_taken(movie_title: str) -> bool:
    return await sync_to_async(
        models.Movie.objects.filter(title=movie_title).exists
    )()


async def check_if_genre_taken(genre_name: str, genre_id: int) -> bool:
    genre = await sync_to_async(
        models.MovieGenre.objects.filter(id=genre_id, name=genre_name).first
    )()

    if genre is not None:
        logger.debug(
            "Genre with given params already in database. No operations."
        )
        return True

    await sync_to_async(
        models.MovieGenre.objects.filter(Q(id=genre_id) | Q(name=genre_name))
        .all()
        .delete
    )()
    logger.debug(
        "Deleting old entries possessing id or name of the new object"
    )
    return False


async def fetch_one_movie(
    session: aiohttp.ClientSession, movie_id: int, movie_title: str
):
    if await check_if_movie_taken(movie_title):
        logger.debug(
            f"Tried to add existing movie: {movie_title}. Operation ignored"
        )
        return
    logger.debug(
        f"Movie {movie_title} not present in database. Fetching missing data from the TMBD API"
    )
    movie_data = await session.get(task_utils.create_movie_query(movie_id))
    movie_data = await movie_data.json()
    assert movie_data["original_title"] == movie_title, (
        f"User tried to add wrong movie!! Requested for "
        f"{movie_title} and server got {movie_data['original_title']}"
    )
    logger.debug(f"Adding movie {movie_title} to the database")

    if not movie_data["release_date"]:
        logger.info(f"Fetcher movie with bad date format: {movie_data}")
        return

    try:
        movie = await sync_to_async(models.Movie.objects.create)(
            title=movie_data["original_title"],
            produce_date=movie_data["release_date"],
            remote_thumbnail=task_utils.create_valid_thumbnail_url(
                movie_data["poster_path"]
            ),
            text=movie_data["overview"],
        )
    except IntegrityError:
        logger.debug(
            "Tried to add movie with exact "
            "same title. Ignored operation to save the fetching process"
        )
        return

    await sync_to_async(movie.genres.set)(
        await sync_to_async(models.MovieGenre.objects.filter)(
            id__in=[el["id"] for el in movie_data["genres"]]
        )
    )


async def fetch_all_movies(session: aiohttp.ClientSession):
    raw_data = await session.get(
        task_utils.create_raw_movie_query(), read_until_eof=True
    )
    movie_data = request_to_python_obj(
        decompress_request(await raw_data.content.read())
    )
    movie_tasks = []

    # limiting for test purposes
    for movie_entry in movie_data[:10_000]:
        movie_tasks.append(
            fetch_one_movie(
                session, movie_entry["id"], movie_entry["original_title"]
            )
        )

    # very expensive!!
    await asyncio.gather(*movie_tasks)
    logger.info("Movie fetching process has finished!")


async def fetch_all_genres(session: aiohttp.ClientSession):
    logger.info("Fetching genre data")
    genres = await session.get(task_utils.create_genres_query())
    assert genres.status == 200, "could not get movie genres"
    genre_list = (await genres.json())["genres"]
    for g in genre_list:
        if not await check_if_genre_taken(g["name"], g["id"]):
            logger.debug(
                f"Genre with name: {g['name']} not present in the "
                "database. Creating new entry."
            )
            await (
                sync_to_async(models.MovieGenre.objects.create)(
                    name=g["name"], id=g["id"]
                )
            )
        else:
            logger.debug(f"Genre with name: {g['name']} already exists")


async def start_data_fetch():
    async with aiohttp.ClientSession() as client:
        # this is cheap. We allow blocking
        genre_task = await fetch_all_genres(client)

        # this is expensive
        movie_task = await fetch_all_movies(client)
