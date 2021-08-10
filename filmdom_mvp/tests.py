from filmdom_mvp import models
from rest_framework import status
from rest_framework.test import (
    APIClient,
    APITestCase,
)
from django.contrib.auth.models import User
from typing import Callable, Tuple, Optional, List
import random
from . import random_data
from secrets import token_urlsafe

# creating dummy server
client = APIClient()


def create_movie(
    title: str = None,
    /,
    produce_date: str = None,
    genres: List[str] = None,
    director: str = None,
    actors: List[str] = None,
) -> models.Movie:
    if title is None:
        title = random.choice(random_data.movie_titles)

    if produce_date is None:
        produce_date = random.choice(random_data.produce_date)

    if genres is None:
        genres = random.sample(
            random_data.produce_date, random.randrange(1, 3)
        )

    if director is None:
        director = random.choice(random_data.directors)

    if actors is None:
        actors = random.sample(random_data.actors, random.randrange(1, 3))

    if models.Movie.objects.filter(title=title).exists():
        title = title + "1"

    models.Movie.objects.filter(title=title).delete()
    models.MovieGenre.objects.filter(name__in=genres).delete()
    models.Actor.objects.filter(name__in=actors).delete()
    models.Director.objects.filter(name=director).delete()

    director = models.Director.objects.create(name=director)

    movie = models.Movie.objects.create(
        title=title,
        produce_date=produce_date,
        director=director,
    )
    movie.genres.set(
        [models.MovieGenre.objects.create(name=name) for name in genres]
    )
    movie.actors.set(
        [models.Actor.objects.create(name=name) for name in actors]
    )
    return movie


def create_dummy_user(
    name: str, password: Optional[str] = None, email: Optional[str] = None
) -> Tuple[models.User, str]:
    if password is None:
        password = name + "pass"

    if email is None:
        email = name + "@ma.il"

    User.objects.filter(username=name).delete()
    rr = client.post(
        "/users/", {"username": name, "email": email, "password": password}
    )
    user = User.objects.filter(username=name).first()

    req = client.post(
        "/api-token-auth/", {"username": name, "password": password}
    ).json()
    token = req["token"]
    return user, token


def create_comments(
    movie: models.Movie, user: models.User, *ratings: int, **kwargs
) -> List[models.Comment]:
    comment_list = []
    for rating in ratings:
        if "text" in kwargs:
            text = kwargs["text"]
        else:
            text = (token_urlsafe(10),)

        comment = models.Comment.objects.create(
            rating=rating,
            commented_movie=movie,
            creator=user,
            text=text,
        )

        comment_list.append(comment)

    return comment_list


class AuthenticationTest(APITestCase):
    """
    Testing if the token authorization method
    is implemented correctly.
    We are ONLY checking the status codes of requests
    and not checking the data itself
    """

    @classmethod
    def setUpTestData(cls):
        client.post(
            "/users/",
            {
                "username": "alice",
                "password": "passwd",
                "email": "alice@aa.pp",
            },
        )

    def test_auth(self):
        good_login = client.login(username="alice", password="passwd")
        bad_login = client.login(username="alice", password="wrong password")
        client.logout()
        self.assertTrue(good_login)
        self.assertFalse(bad_login)

    def test_auth_integrity(self):
        res = client.post(
            "/api-token-auth/", {"username": "alice", "password": "passwd"}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        token = res.json()["token"]
        res = client.get("/auth/", HTTP_AUTHORIZATION="Token " + token)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_bad_password(self):
        res = client.post(
            "/api-token-auth/",
            {"username": "alice", "password": "wrong password"},
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ReadingPublicDataTest(APITestCase):
    def test_reading_comments(self):
        alice = User.objects.create_user("alice", "ali@ce.com", "alicepass")
        movie = create_movie()

        comment = models.Comment.objects.create(
            rating=3, text="nice movie", commented_movie=movie, creator=alice
        )
        # testing list view
        res = client.get("/comments/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get(f"/comments/{comment.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

    def test_reading_movies(self):
        movie = create_movie()

        # testing list view
        res = client.get("/movies/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get(f"/movies/{movie.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

    def test_reading_directors(self):
        director = models.Director.objects.create(name="tarantino")
        # testing list view
        res = client.get("/directors/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get(f"/directors/{director.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

    def test_reading_genres(self):
        genre = models.MovieGenre.objects.create(name="drama")
        # testing list view
        res = client.get("/genres/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get(f"/genres/{genre.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

    def test_reading_actors(self):
        actor = models.Actor.objects.create(name="robert de niro")
        # testing list view
        res = client.get("/actors/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get(f"/actors/{actor.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

    def test_modify_public_data(self):
        res = client.post(
            "/movies/", {"title": "django", "produce_date": "2020-12-10"}
        )
        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED, res.content
        )
        res = client.post("/genres/", {"name": "drama"})
        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED, res.content
        )
        res = client.post("/actors/", {"name": "de niro"})
        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED, res.content
        )


class AuthorizationTest(APITestCase):
    """
    Testing if permissions
    policies are enforced
    """

    def setUp(self):
        self.username = "admin"
        self.password = "admin_passw"

        self.alice = User.objects.create_user(
            "alice", "ali@ce.com", "alicepass"
        )

        self.admin = User.objects.create_superuser(
            self.username, "test@example.com", self.password
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_only_admin_operations(self):
        """
        Only admin should be able to see list of all
        the registered users on the website
        """
        client.force_authenticate(user=self.admin)
        request = client.get("/users/")
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        client.force_authenticate(user=None)
        request = client.get("/users/")
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_comment_by_loged_user(self):
        movie = create_movie()
        alice_user, alice_token = create_dummy_user("alice")
        res = client.post(
            "/comments/",
            {
                "rating": 1,
                "commented_movie": movie.id,
                "creator": alice_user.id,
                "text": "not nice movie",
            },
            HTTP_AUTHORIZATION="Token " + alice_token,
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        client.logout()  # just to be sure..

        res = client.post(
            "/comments/",
            {
                "rating": 4,
                "commented_movie": movie.id,
                "creator": alice_user.id,
                "text": "totally fake comment",
            },
        )
        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED, res.content
        )

    def test_delete_by_authorized_user(self):
        movie = create_movie()
        alice_user, alice_token = create_dummy_user("alice")

        res = client.post(
            "/comments/",
            {
                "rating": 1,
                "commented_movie": movie.id,
                "creator": alice_user.id,
                "text": "not nice movie",
            },
            HTTP_AUTHORIZATION="Token " + alice_token,
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        res = client.get(f"/comments/{movie.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        res = client.delete(
            f"/comments/{movie.id}/", HTTP_AUTHORIZATION="Token " + alice_token
        )
        self.assertEqual(
            res.status_code, status.HTTP_204_NO_CONTENT, res.content
        )

        res = client.get(f"/comments/{movie.id}/")
        self.assertEqual(
            res.status_code, status.HTTP_404_NOT_FOUND, res.content
        )

    def test_delete_by_unauthorized_user(self):
        movie = create_movie()
        alice_user, alice_token = create_dummy_user("alice")
        _, bob_token = create_dummy_user("bob")

        comm = models.Comment.objects.create(
            rating=2,
            text="lorem ipsum",
            commented_movie=movie,
            creator=alice_user,
        )

        # bob (not owner) tries to delete the commment
        res = client.delete(
            f"/comments/{comm.id}/", HTTP_AUTHORIZATION="Token " + bob_token
        )
        self.assertEqual(
            res.status_code, status.HTTP_403_FORBIDDEN, res.content
        )

        # alice deletes the comment
        res = client.delete(
            f"/comments/{comm.id}/", HTTP_AUTHORIZATION="Token " + alice_token
        )
        self.assertEqual(
            res.status_code, status.HTTP_204_NO_CONTENT, res.content
        )

    def test_user_owner_operations(self):
        ...


class MovieDataTest(APITestCase):
    def tearDown(self):
        models.Movie.objects.all().delete()
        models.Comment.objects.all().delete()
        models.User.objects.all().delete()

    def test_turn_off_pagination(self):
        no_of_movies = 20
        for i in range(no_of_movies):
            create_movie(f"pagi title no.:{i}")

        res = client.get("/movies/", data={"limit": 100})
        self.assertNotIn("results", res.json())

        res = client.get("/movies/")
        self.assertIn("results", res.json())

    def test_get_limit(self):
        no_of_movies = 20
        limit_val = 5
        for i in range(no_of_movies):
            create_movie(f"title no.:{i}")

        res = client.get("/movies/", data={"limit": limit_val})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(
            len(res.json()),
            limit_val,
            f"Movies: {len(res.json())} | should be: {limit_val}",
        )

    def test_movie_sorting_rating(self):
        alice, _ = create_dummy_user("alice")

        movie1 = create_movie("movie1")
        movie2 = create_movie("movie2")
        movie3 = create_movie("movie3")

        create_comments(movie1, alice, 4, 3, 4, 3, 2)
        create_comments(movie2, alice, 1, 1, 1, 2, 1)
        create_comments(movie3, alice, 4, 5, 5, 5, 5)
        correct_order = ["movie3", "movie1", "movie2"]

        res = client.get("/movies/", data={"sort_method": "best"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        title_list = [m["title"] for m in res.json()["results"]]
        self.assertEqual(
            title_list,
            correct_order,
            f"result: {title_list}, should be {correct_order}",
        )

        res = client.get("/movies/", data={"sort_method": "worst"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        title_list = [m["title"] for m in res.json()["results"]]
        self.assertEqual(
            title_list,
            correct_order[::-1],
            f"result: {title_list}, should be {correct_order[::-1]}",
        )

    def test_movie_sorting_date(self):
        create_movie("movie1", produce_date="2005-12-30")
        create_movie("movie2", produce_date="1980-05-13")
        create_movie("movie3", produce_date="2020-01-02")
        correct_order = ["movie3", "movie1", "movie2"]

        res = client.get("/movies/", data={"sort_method": "newest"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        title_list = [m["title"] for m in res.json()["results"]]
        self.assertEqual(
            title_list,
            correct_order,
            f"result: {title_list}, should be {correct_order}",
        )

        res = client.get("/movies/", data={"sort_method": "oldest"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        title_list = [m["title"] for m in res.json()["results"]]
        self.assertEqual(
            title_list,
            correct_order[::-1],
            f"result: {title_list}, should be {correct_order[::-1]}",
        )

    def test_movie_sorting_popularity(self):
        alice, _ = create_dummy_user("alice")

        movie1 = create_movie("movie1")
        movie2 = create_movie("movie2")
        movie3 = create_movie("movie3")

        create_comments(movie1, alice, 1, 1, 1, 1, 1)
        create_comments(movie2, alice, 1, 1, 1)
        create_comments(movie3, alice, 1, 1, 1, 1, 1, 1, 1, 1)
        correct_order = ["movie3", "movie1", "movie2"]

        res = client.get("/movies/", data={"sort_method": "most_popular"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        title_list = [m["title"] for m in res.json()["results"]]
        self.assertEqual(
            title_list,
            correct_order,
            f"result: {title_list}, should be {correct_order}",
        )

        res = client.get("/movies/", data={"sort_method": "least_popular"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        title_list = [m["title"] for m in res.json()["results"]]
        self.assertEqual(
            title_list,
            correct_order[::-1],
            f"result: {title_list}, should be {correct_order[::-1]}",
        )

    def test_movie_random(self):
        create_movie()
        create_movie()
        create_movie()

        res = client.get("/movies/", data={"sort_method": "random"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(len(res.json()["results"]), 3, res.json()["results"])

    def test_movie_title_subseq(self):
        m1 = create_movie("0000movie000")
        m2 = create_movie("aaaaaaa")
        m3 = create_movie("movie000")
        m4 = create_movie("MoVIe")

        # setting limit so we are not paginating the results
        res = client.get(
            "/movies/", data={"title_like": "movie", "limit": 100}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(len(res.json()), 3, res.json())


class CommentTest(APITestCase):
    def tearDown(self):
        models.Movie.objects.all().delete()
        models.Comment.objects.all().delete()
        models.User.objects.all().delete()

    def test_sort_date(self):
        m = create_movie()
        alice, _ = create_dummy_user("alice")

        create_comments(m, alice, 3, text="comment1")
        create_comments(m, alice, 4, text="comment2")
        create_comments(m, alice, 1, text="comment3")
        correct_order = ["comment3", "comment2", "comment1"]

        res = client.get("/comments/", data={"sort_method": "newest"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        title_list = [m["text"] for m in res.json()["results"]]
        self.assertEqual(
            title_list,
            correct_order,
            f"result: {title_list}, should be {correct_order}. {res.json()['results']}",
        )

        res = client.get("/comments/", data={"sort_method": "oldest"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        title_list = [m["text"] for m in res.json()["results"]]
        self.assertEqual(
            title_list,
            correct_order[::-1],
            f"result: {title_list}, should be {correct_order[::-1]}",
        )

    def test_filter_by_user(self):
        m = create_movie()
        alice, _ = create_dummy_user("alice")
        bob, _ = create_dummy_user("bob")

        create_comments(m, alice, 3, create_date="2000-10-01", text="comment1")
        create_comments(
            m, alice, 1, create_date="2000-10-29", text="iiicomment1"
        )
        create_comments(m, bob, 4, create_date="1990-04-11", text="comment2")

        res = client.get("/comments/", data={"user": alice.username})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(2, len(res.json()["results"]), res.json()["results"])

        res = client.get("/comments/", data={"user": bob.username})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(1, len(res.json()["results"]), res.json()["results"])

        # filter by id
        res = client.get("/comments/", data={"user_id": alice.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(2, len(res.json()["results"]), res.json()["results"])

    def test_filter_by_movie(self):
        m1 = create_movie("movie1")
        m2 = create_movie("movie2")
        m3 = create_movie("aaaaaaaaaaa")
        alice, _ = create_dummy_user("alice")

        create_comments(
            m1, alice, 3, create_date="2000-10-01", text="comment1"
        )
        create_comments(
            m2, alice, 4, create_date="1990-04-11", text="comment2"
        )
        create_comments(
            m1, alice, 1, create_date="2018-11-20", text="comment3"
        )
        create_comments(
            m3, alice, 1, create_date="2018-11-20", text="comment3"
        )

        res = client.get("/comments/", data={"title": m1.title})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(2, len(res.json()["results"]), res.json())

        res = client.get("/comments/", data={"title": m2.title})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(1, len(res.json()["results"]), res.json())

        # filter by id
        res = client.get("/comments/", data={"movie_id": m2.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(1, len(res.json()["results"]), res.json())

        # filter by subsequence
        res = client.get("/comments/", data={"title_like": "movie"})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(3, len(res.json()["results"]), res.json()["results"])

    def test_get_limit(self):
        movie = create_movie()
        alice, _ = create_dummy_user("alice")
        no_of_comments = 20

        create_comments(
            movie, alice, *tuple([1 for i in range(no_of_comments)])
        )

        res = client.get("/comments/", data={"limit": 10})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(10, len(res.json()), res.json())

        res = client.get("/comments/", data={"limit": 20})
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(20, len(res.json()), res.json())


class DataflowTest(APITestCase):
    """
    Testing cascades and internal data stuff
    """

    def test_comment_cascades(self):
        u1, _ = create_dummy_user("bob")

        m1 = create_movie()
        m2 = create_movie()

        create_comments(m1, u1, 1, 2, 3, 4)
        n_comments = models.Comment.objects.count()
        self.assertEqual(4, n_comments, f"Ori: {n_comments} | should be 4")

        u1.delete()
        n_comments = models.Comment.objects.count()
        self.assertEqual(0, n_comments, f"Ori: {n_comments} | should be 0")

        u1, _ = create_dummy_user("bob")
        create_comments(m1, u1, 1, 2, 3, 4)
        m1.delete()
        n_comments = models.Comment.objects.count()
        self.assertEqual(0, n_comments, f"Ori: {n_comments} | should be 0")
