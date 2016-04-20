from django.db import models

from .game import Game
from .resident import Resident


class Hut(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='huts'
    )
    resident = models.ForeignKey(
        Resident, on_delete=models.DO_NOTHING, related_name='+'
    )

    position = models.IntegerField()
    time_eliminated = models.DateTimeField(blank=True, null=True, default=None)
