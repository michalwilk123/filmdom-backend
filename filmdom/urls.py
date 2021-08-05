from django.urls import include, path
from rest_framework import routers
from filmdom_mvp import views
from filmdom import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib import admin
from filmdom_mvp import models

router = routers.DefaultRouter()
router.register("users", views.UserViewSet)
router.register("movies", views.MovieViewSet)
router.register("comments", views.CommentViewSet)
router.register("directors", views.DirectorViewSet)
router.register("actors", views.ActorViewSet)
router.register("genres", views.MovieGenreViewSet)

admin.site.register(models.Actor)
admin.site.register(models.MovieGenre)
admin.site.register(models.Movie)
admin.site.register(models.Comment)
admin.site.register(models.Director)

urlpatterns = [
    path("", include(router.urls)),
    path('admin/', admin.site.urls),
    path("api-token-auth/", obtain_auth_token),
    path("auth/", views.AuthTestView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
