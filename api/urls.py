from django.conf.urls import url, include

from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'games', views.GameViewSet)
router.register(
    prefix=r'games/(?P<game_id>[0-9]+)/players',
    viewset=views.PlayerViewSet,
    base_name='players'
)

urlpatterns = router.urls
