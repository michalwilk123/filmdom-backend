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
            "/api-token-auth/", {"username": "alice", "password": "wrong password"}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reading_public_data(self):
        ...
    
    def test_owner_modify_data(self):
        ...


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
