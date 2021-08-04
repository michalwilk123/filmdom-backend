from filmdom_mvp import models
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, force_authenticate
from django.contrib.auth.models import User

# creating dummy server
client = APIClient()


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

    def test_owner_modify_data(self):
        ...


class ReadingPublicDataTest(APITestCase):
    def test_reading_comments(self):
        genre = models.MovieGenre.objects.create(name="lol")
        actor = models.Actor.objects.create(name="lol")
        director = models.Director.objects.create(name="tarantino")
        alice = User.objects.create_user("alice", "ali@ce.com", "alicepass")

        movie = models.Movie.objects.create(
            title="Lorem ipsum",
            produce_date="2000-01-31",
            director=director,
        )
        movie.genres.set([genre])
        movie.actors.set([actor])
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
        genre = models.MovieGenre.objects.create(name="lol")
        actor = models.Actor.objects.create(name="lol")
        director = models.Director.objects.create(name="tarantino")
        movie = models.Movie.objects.create(
            title="django", produce_date="2020-12-10", director=director
        )

        movie.genres.set([genre])
        movie.actors.set([actor])
        # testing list view
        res = client.get("/movies/")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)

        # testing detail view
        res = client.get("/movies/1/")
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
        res = client.post("/comments/", {"rating": 3, "text": "nice movie"})
        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED, res.content
        )
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

        User.objects.create_user("alice", "ali@ce.com", "alicepass")
        User.objects.create_user("bob", "bob@tt.com", "bobpass")

        self.admin = User.objects.create_superuser(
            self.username, "test@example.com", self.password
        )

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


class MovieDataTest(APITestCase):
    ...


class CommentTest(APITestCase):
    ...


class DataflowTest(APITestCase):
    ...
