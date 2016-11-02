from django.db import models
from rest_framework import status

from .game import Game
from .role import Role

from ..exceptions import APIException, APIExceptionCode


class Resident(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='residents'
    )
    role = models.ForeignKey(
        Role, on_delete=models.DO_NOTHING, related_name='+'
    )

    time_eliminated = models.DateTimeField(blank=True, null=True, default=None)

    action = None

    def use_action(self, player, targets=None, *args, **kwargs):
        if bool(self.time_eliminated):
            raise APIException(
                'Eliminated roles cannot perform any further actions',
                APIExceptionCode.ACTION_INVALID_ACTOR,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        similar_action = self.game.active_turn.actions.filter(
            models.Q(player=player) | models.Q(resident=self)
        ).first()

        if similar_action:
            if similar_action.player == player:
                raise APIException(
                    'Player has already used a different action this turn',
                    APIExceptionCode.ACTION_ACTOR_MULTIPLE_ACTION,
                    http_code=status.HTTP_400_BAD_REQUEST
                )

            if similar_action.resident == self:
                raise APIException(
                    'Actions can only be used once per turn',
                    APIExceptionCode.ACTION_ALREADY_USED,
                    http_code=status.HTTP_400_BAD_REQUEST
                )

        self.action = self.game.active_turn.actions.create(
            player=player, resident=self
        )
