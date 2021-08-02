from django.contrib.auth.models import User, Group
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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class DirectorViewSet(viewsets.ModelViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer
    permission_classes = [permissions.IsAdminUser]


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MovieGenreViewSet(viewsets.ModelViewSet):
    queryset = MovieGenre.objects.all()
    serializer_class = MovieGenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class HelloViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response("you are logged in")
