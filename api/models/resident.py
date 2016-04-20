from django.db import models

from .game import Game
from .role import Role


class Resident(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='residents'
    )
    role = models.ForeignKey(
        Role, on_delete=models.DO_NOTHING, related_name='+'
    )

    time_eliminated = models.DateTimeField(blank=True, null=True, default=None)
