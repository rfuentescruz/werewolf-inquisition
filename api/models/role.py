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

    CUSTOM_NAMES = {
        'APPRENTICE_SEER': 'Apprentice Seer',
        'WOLF_CUB': 'Wolf Cub'
    }


class Role(models.Model):
    name = models.CharField(max_length=100, null=False)

    role = models.CharField(
        max_length=20, choices=Roles.choices(), unique=True, null=False
    )

    team = models.CharField(max_length=10, choices=Teams.choices())
