from django.conf.urls import url
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'games', views.GameViewSet)
router.register(
    prefix=r'games/(?P<game_id>[0-9]+)/players',
    viewset=views.PlayerViewSet,
    base_name='players'
)
router.register(
    prefix=r'games/(?P<game_id>[0-9]+)/residents',
    viewset=views.ResidentViewSet,
    base_name='residents'
)
router.register(
    prefix=r'games/(?P<game_id>[0-9]+)/turns',
    viewset=views.TurnViewSet,
    base_name='turns'
)

urlpatterns = [
    url(
        r'games/(?P<game_id>[0-9]+)/actions/(?P<role>.*)/',
        views.ActionAPIView.as_view()
    )
]

urlpatterns += router.urls
