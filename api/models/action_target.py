from django.db import models

from .action import Action
from .hut import Hut
from .player import Player


class ActionTarget(models.Model):
    action = models.ForeignKey(
        Action, on_delete=models.DO_NOTHING, related_name='targets'
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        default=None,
        related_name='+'
    )
    hut = models.ForeignKey(
        Hut,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        default=None,
        related_name='+'
    )
