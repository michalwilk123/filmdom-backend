from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


class MovieGenre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=256, unique=True)
    added_date = models.DateField(auto_now_add=True)
    produce_date = models.DateField()
    image_height = models.PositiveIntegerField(
        validators=[MaxValueValidator(600), MinValueValidator(100)],
        default=300,
    )
    image_width = models.PositiveIntegerField(
        validators=[MaxValueValidator(400), MinValueValidator(100)],
        default=200,
    )

    thumbnail = models.ImageField(
        width_field="image_height",
        height_field="image_width",
        default="noImageAvailable.png",
        upload_to="uploaded_images/",
    )

    genres = models.ManyToManyField(MovieGenre, blank=True)
    director = models.ForeignKey(
        Director, on_delete=models.SET_NULL, null=True, blank=True
    )
    actors = models.ManyToManyField(Actor)


class Comment(models.Model):
    rating = models.FloatField(
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )
    created = models.DateField(auto_now_add=True)
    text = models.CharField(blank=True, null=True, max_length=2048)

    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    commented_movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="comments"
    )
