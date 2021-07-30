from django.contrib.auth.models import User, Group
from .models import MovieGenre, Movie, Director, Actor, Comment
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class MovieSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movie
        # fields = [
        #     "url",
        #     "title",
        #     "added_date",
        #     "produce_date",
        #     # "thumbnail",
        #     "director",
        #     "actor",
        # ]
        fields = "__all__"


class MovieGenreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MovieGenre
        fields = ["url", "name"]


class DirectorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Director
        fields = ["url", "name"]


class ActorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Actor
        fields = ["name"]


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
