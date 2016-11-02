from django.db import models

from .player import Player
from .turn import Turn
from .hut import Hut


class Vote(models.Model):
    turn = models.ForeignKey(
        Turn, on_delete=models.DO_NOTHING, related_name='votes'
    )
    player = models.ForeignKey(
        Player, on_delete=models.DO_NOTHING, related_name='votes'
    )
    hut = models.ForeignKey(
        Hut,
        on_delete=models.DO_NOTHING,
        related_name='votes',
        blank=True, null=True, default=None
    )

    time_created = models.DateTimeField(auto_now_add=True)
    time_removed = models.DateTimeField(null=True, blank=True, default=None)
