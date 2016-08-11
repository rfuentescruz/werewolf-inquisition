from django.db import models

from .game import Game
from .resident import Resident


class Hut(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='huts'
    )
    resident = models.OneToOneField(
        Resident, on_delete=models.DO_NOTHING, related_name='hut'
    )

    position = models.IntegerField()
    is_visited = models.BooleanField(blank=False, null=False, default=False)
    time_eliminated = models.DateTimeField(blank=True, null=True, default=None)
