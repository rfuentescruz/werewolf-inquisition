from django.db import models

from .game import Game, Teams
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


class Resident(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='residents'
    )
    role = models.ForeignKey(
        Role, on_delete=models.DO_NOTHING, related_name='+'
    )

    time_eliminated = models.DateTimeField(blank=True, null=True, default=None)


class Hut(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='huts'
    )
    resident = models.ForeignKey(
        Resident, on_delete=models.DO_NOTHING, related_name='+'
    )

    position = models.IntegerField()
    time_eliminated = models.DateTimeField(blank=True, null=True, default=None)
