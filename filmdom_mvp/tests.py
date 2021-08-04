from filmdom_mvp import models
from rest_framework import status
from rest_framework.test import (
    APIClient,
    APITestCase,
    APIRequestFactory,
)
from django.contrib.auth.models import User
from typing import Callable, Tuple, Optional, List
import random
from . import random_data

# creating dummy server
client = APIClient()
factory = APIRequestFactory()


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

    if (movie := models.Movie.objects.filter(title=title)).exists():
        return movie

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
) -> Tuple[User, str]:
    if password is None:
        password = name + "pass"

    if email is None:
        password = name + "mail"

    User.objects.filter(username=name).delete()
    user = User.objects.create_user(name, email, password)

    req = client.post(
        "/api-token-auth/", {"username": name, "password": password}
    ).json()
    token = req["token"]
    return user, token

def validate_sort(collection:List, key:Callable)->bool:
    return False

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

        models.Comment.objects.create(
            rating=3, text="nice movie", commented_movie=movie, creator=alice
        )
        # testing list view
        res = client.get("/comments/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get("/comments/1/")
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
        models.Director.objects.create(name="tarantino")
        # testing list view
        res = client.get("/directors/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get("/directors/1/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

    def test_reading_genres(self):
        models.MovieGenre.objects.create(name="drama")
        # testing list view
        res = client.get("/genres/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get("/genres/1/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

    def test_reading_actors(self):
        models.Actor.objects.create(name="robert de niro")
        # testing list view
        res = client.get("/actors/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get("/actors/1/")
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
        create_movie()
        alice_user, alice_token = create_dummy_user("alice")
        res = client.post(
            "/comments/",
            {
                "rating": 1,
                "commented_movie": "/movies/1/",
                "creator": f"/users/{alice_user.id}/",
                "text": "not nice movie",
            },
            HTTP_AUTHORIZATION="Token " + alice_token,
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        client.logout()

        res = client.post(
            "/comments/",
            {
                "rating": 4,
                "commented_movie": "/movies/1/",
                "creator": "/users/1/",
                "text": "totally fake comment",
            },
        )
        self.assertEqual(
            res.status_code, status.HTTP_400_BAD_REQUEST, res.content
        )

    def test_delete_by_authorized_user(self):
        movie = create_movie()
        alice_user, alice_token = create_dummy_user("alice")

        res = client.post(
            "/comments/",
            {
                "rating": 1,
                "commented_movie": f"/movies/{movie.id}/",
                "creator": f"/users/{alice_user.id}/",
                "text": "not nice movie",
            },
            HTTP_AUTHORIZATION="Token " + alice_token,
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        res = client.get("/comments/1/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        res = client.delete(
            "/comments/1/", HTTP_AUTHORIZATION="Token " + alice_token
        )
        self.assertEqual(
            res.status_code, status.HTTP_204_NO_CONTENT, res.content
        )

        res = client.get("/comments/1/")
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


class CommentTest(APITestCase):
    def test_comment_sorting_popularity(self):
        ...

    def test_comment_sorting_date(self):
        ...

    def test_comment_sorting_rating(self):
        ...

    def test_comment_random(self):
        ...

    def test_get_limit(self):
        ...


class DataflowTest(APITestCase):
    """
    Testing cascades
    """
    ...
