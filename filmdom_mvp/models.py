from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


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
    title = models.CharField(max_length=256)
    added_date = models.DateField(auto_now_add=True)
    produce_date = models.DateField()
    image_height = models.PositiveIntegerField(
        validators=[MaxValueValidator(600), MinValueValidator(100)]
    )
    image_width = models.PositiveIntegerField(
        validators=[MaxValueValidator(400), MinValueValidator(100)]
    )

    thumbnail = models.ImageField(
        width_field="image_height",
        height_field="image_width",
        default="noImageAvailable.png",
        upload_to="uploaded_images/",
    )

    genres = models.ManyToManyField(MovieGenre, blank=True)
    director = models.ForeignKey(
        Director, on_delete=models.CASCADE, default="Anon"
    )
    actor = models.ManyToManyField(Actor, blank=True)


class Comment(models.Model):
    rating = models.FloatField(
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )
    created = models.DateField(auto_now_add=True)
    text = models.CharField(blank=True, null=True, max_length=2048)

    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # commented_movie = models.OneToOneField(Movie, on_delete=models.CASCADE)
