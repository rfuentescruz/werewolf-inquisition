from django.db import models

from rest_framework import status

from .game import Game
from .phase import Phases
from .player import Player

from ..exceptions import APIException, APIExceptionCode


class Turn(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='turns'
    )
    number = models.IntegerField()
    is_active = models.BooleanField(default=True)

    grand_inquisitor = models.ForeignKey(
        Player, on_delete=models.DO_NOTHING, related_name='+'
    )
    current_phase = models.IntegerField(
        choices=Phases.choices(),
        blank=True, null=True, default=Phases.DAY.value
    )
    current_player = models.ForeignKey(
        Player,
        blank=True, null=True, default=None, on_delete=models.SET_NULL,
        related_name='+'
    )

    time_created = models.DateTimeField(auto_now_add=True)

    def end(self):
        if not self.is_active:
            raise APIException(
                'Cannot end a turn that has already ended',
                APIExceptionCode.TURN_ALREADY_ENDED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        grand_inquisitor = self.game.get_next_player(self.grand_inquisitor)

        self.is_active = False
        self.save()

        new_turn = self.game.turns.create(
            number=self.number + 1,
            grand_inquisitor=grand_inquisitor,
            current_phase=Phases.DAY.value,
            current_player=grand_inquisitor
        )

        return new_turn
