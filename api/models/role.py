from django.db import models

from .team import Teams
from .choice_enum import ChoiceEnum


class Roles(ChoiceEnum):
    APPRENTICE_SEER = 'apprentice_seer'
    BODYGUARD = 'bodyguard'
    CURSED = 'cursed'
    HUNTER = 'hunter'
    MASON = 'mason'
    MAYOR = 'mayor'
    MINION = 'minion'
    PRINCE = 'prince'
    SEER = 'seer'
    SORCERER = 'sorcerer'
    TROUBLEMAKER = 'troublemaker'
    VILLAGER = 'villager'
    WEREWOLF = 'werewolf'
    WITCH = 'witch'
    WOLF_CUB = 'wolf_cub'

    @classmethod
    def get_choice_label(cls, name):
        return ' '.join(
            [s.capitalize() for s in name.split('_')]
        )


class Role(models.Model):
    name = models.CharField(max_length=100, null=False)

    role = models.CharField(
        max_length=20, choices=Roles.choices(), unique=True, null=False
    )

    team = models.CharField(max_length=10, choices=Teams.choices())

    max_count = models.PositiveSmallIntegerField(
        null=True, blank=True, default=1
    )

    value = models.SmallIntegerField(null=False, default=0)
