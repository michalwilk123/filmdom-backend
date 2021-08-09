from django.contrib.auth.models import User, Group
from .models import MovieGenre, Movie, Director, Actor, Comment
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            email=validated_data["email"], username=validated_data["username"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class MovieSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    director_name = serializers.ReadOnlyField(source="director.name")

    class Meta:
        model = Movie
        fields = "__all__"


class MovieGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieGenre
        fields = "__all__"


class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = "__all__"


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source="creator.username")
    movie_title = serializers.ReadOnlyField(source="commented_movie.title")

    class Meta:
        model = Comment
        fields = "__all__"
