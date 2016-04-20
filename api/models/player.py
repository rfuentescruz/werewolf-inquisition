from datetime import datetime

from django.contrib.auth.models import User

from django.db import models
from rest_framework import status

from ..exceptions import APIException, APIExceptionCode

from .game import Game
from .team import Teams


class PlayerManager(models.Manager):
    def get_queryset(self):
        # Eagerly-load `User` data since we won't be using the `Player` model
        # by itself anyways
        return super(PlayerManager, self).get_queryset().select_related('user')


class Player(models.Model):
    # Override default manager
    objects = PlayerManager()

    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='players'
    )

    is_owner = models.BooleanField(default=False)

    team = models.CharField(
        max_length=10,
        choices=Teams.choices(),
        default=Teams.VILLAGER.value
    )
    position = models.IntegerField(default=1)

    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='+'
    )

    time_created = models.DateTimeField(auto_now_add=True)
    time_withdrawn = models.DateTimeField(blank=True, null=True, default=None)

    def has_left(self):
        if not self.time_withdrawn:
            return False
        return True

    def leave_game(self):
        if self.has_left():
            raise APIException(
                'Player already left',
                APIExceptionCode.PLAYER_ALREADY_LEFT,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        if self.game.has_started():
            raise APIException(
                'Unable to leave game. Game has already started',
                APIExceptionCode.GAME_ALREADY_STARTED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        if self.game.has_ended():
            raise APIException(
                'Game has already ended',
                APIExceptionCode.GAME_ALREADY_ENDED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        self.time_withdrawn = datetime.now()
        self.save()
