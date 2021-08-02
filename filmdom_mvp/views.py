from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
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


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class DirectorViewSet(viewsets.ModelViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class MovieGenreViewSet(viewsets.ModelViewSet):
    queryset = MovieGenre.objects.all()
    serializer_class = MovieGenreSerializer
