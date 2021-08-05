from django.contrib.auth.models import User, Group
from django.db.models import Avg, Count, Subquery
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from filmdom_mvp.serializers import (
    ActorSerializer,
    CommentSerializer,
    DirectorSerializer,
    MovieGenreSerializer,
    MovieSerializer,
    UserSerializer,
    GroupSerializer,
    Actor,
    Director,
    MovieGenre,
    Movie,
    Comment,
)
from filmdom_mvp.permissions import (
    IsOwnerOrReadOnly,
    CreationAllowed,
    ReadOnly,
)
import random


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [CreationAllowed | permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all().order_by("title")
    serializer_class = MovieSerializer
    permission_classes = [ReadOnly | permissions.IsAdminUser]

    @staticmethod
    def validate_limit(limit) -> bool:
        if limit is None:
            return False

        try:
            limit = int(limit)
        except ValueError:
            return False

        if limit < 1:
            return False

        return True

    def get_queryset(self):
        limit = self.request.query_params.get("limit")
        sort_method = self.request.query_params.get("sort_method")
        queryset = []

        if sort_method == "best":
            queryset = Movie.objects.annotate(
                average_rating=Avg("comments__rating")
            ).order_by("-average_rating")
        elif sort_method == "worst":
            queryset = Movie.objects.annotate(
                average_rating=Avg("comments__rating")
            ).order_by("average_rating")
        elif sort_method == "most_popular":
            queryset = Movie.objects.annotate(
                no_of_comments=Count("comments")
            ).order_by("-no_of_comments")
        elif sort_method == "least_popular":
            queryset = Movie.objects.annotate(
                no_of_comments=Count("comments")
            ).order_by("no_of_comments")
        elif sort_method == "newest":
            queryset = Movie.objects.all().order_by("-produce_date")
        elif sort_method == "oldest":
            queryset = Movie.objects.all().order_by("produce_date")
        elif sort_method == "random":
            queryset = sorted(
                Movie.objects.all(), key=lambda x: random.random()
            )
        else:
            queryset = Movie.objects.all().order_by("title")

        if MovieViewSet.validate_limit(limit):
            self._paginator = None
            queryset = queryset[: int(limit)]

        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all().order_by("created")
        limit = self.request.query_params.get("limit")
        order_by = self.request.query_params.get("order_by")
        title = self.request.query_params.get("title")
        movie_id = self.request.query_params.get("title")
        user = self.request.query_params.get("user")
        user_id = self.request.query_params.get("user_id")
        title_like = self.request.query_params.get("title_like")

        if title is not None:
            queryset = queryset.select_related("Movie").filter(title=title)
            return queryset
        elif title_like not in (None, ""):
            queryset = queryset.select_related("Movie").filter(
                title__icontains=title_like
            )

        if user is not None:
            queryset = queryset.select_related("User").filter(username=user)
        elif user_id is not None:
            try:
                user_id = int(user_id)
                queryset = queryset.filter(user_id=user_id)
            except ValueError:
                pass

        if order_by is not None:
            if order_by == "newest":
                # by default we sort by date so we just ignore
                # the parameter
                ...
            elif order_by == "oldest":
                queryset = queryset[::-1]

        if limit is not None and limit in range(1, 100):
            queryset = queryset[:limit]

        return queryset


class DirectorViewSet(viewsets.ModelViewSet):
    queryset = Director.objects.all().order_by("name")
    serializer_class = DirectorSerializer
    permission_classes = [ReadOnly | permissions.IsAdminUser]


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all().order_by("name")
    serializer_class = ActorSerializer
    permission_classes = [ReadOnly | permissions.IsAdminUser]


class MovieGenreViewSet(viewsets.ModelViewSet):
    queryset = MovieGenre.objects.all().order_by("name")
    serializer_class = MovieGenreSerializer
    permission_classes = [ReadOnly | permissions.IsAdminUser]


class AuthTestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response("Your credentials were accepted")
