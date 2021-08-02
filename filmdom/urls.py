from django.urls import include, path
from rest_framework import routers
from filmdom_mvp import views
from filmdom import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register("users", views.UserViewSet)
router.register("movies", views.MovieViewSet)
router.register("comments", views.CommentViewSet)
router.register("directors", views.DirectorViewSet)
router.register("actors", views.ActorViewSet)
router.register("genres", views.MovieGenreViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-token-auth/", obtain_auth_token),
    path("hello/", views.HelloViewSet.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
