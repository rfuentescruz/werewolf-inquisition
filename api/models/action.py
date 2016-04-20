from django.db import models

from .player import Player
from .turn import Turn


class Action(models.Model):
    turn = models.ForeignKey(
        Turn, on_delete=models.DO_NOTHING, related_name='actions'
    )
    player = models.ForeignKey(
        Player, on_delete=models.DO_NOTHING, related_name='actions'
    )
    resident = models.ForeignKey(
        'Resident',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        default=None,
        related_name='+'
    )

    time_created = models.DateTimeField(auto_now_add=True)
