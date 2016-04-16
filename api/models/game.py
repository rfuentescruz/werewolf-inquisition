import math

from datetime import datetime
from enum import Enum
from random import shuffle

from django.contrib.auth.models import User
from django.db import models
from rest_framework import status

from .choice_enum import ChoiceEnum
from ..exceptions import APIException, APIExceptionCode

class Teams(ChoiceEnum, Enum):
    VILLAGER = 'villager'
    WEREWOLF = 'werewolf'


class Phases(ChoiceEnum, Enum):
    INITIAL = 0
    DAY = 1
    VOTING = 2
    NIGHT = 3


class Game(models.Model):
    MIN_PLAYERS = 3
    MAX_PLAYERS = 12

    owner = models.ForeignKey(
        'Player',
        on_delete=models.DO_NOTHING,
        related_name='+',
        # Chicken-and-egg, `Player` models are defined by `Game` models and we
        # need the game first to know the owning player.
        blank=True, null=True, default=None
    )

    active_turn = models.ForeignKey(
        'Turn',
        blank=True, null=True, default=None, on_delete=models.SET_NULL,
        related_name='+'
    )
    winning_team = models.CharField(
        max_length=10, choices=Teams.choices(),
        blank=True, null=True, default=None
    )

    time_created = models.DateTimeField(auto_now_add=True)
    time_started = models.DateTimeField(blank=True, null=True, default=None)
    time_ended = models.DateTimeField(blank=True, null=True, default=None)

    def has_started(self):
        if not self.time_started:
            return False
        return True

    def has_ended(self):
        if not self.time_ended:
            return False
        return True

    def join(self, user):
        if self.has_started():
            raise APIException(
                'Unable to join game. Game has already started',
                APIExceptionCode.GAME_ALREADY_STARTED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        if self.has_ended():
            raise APIException(
                'Unable to join game. Game has already ended',
                APIExceptionCode.GAME_ALREADY_ENDED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        player = None
        try:
            player = self.get_player(username=user.username)
        except Player.DoesNotExist:
            pass
        else:
            if not player.has_left():
                raise APIException(
                    'You have already joined this game',
                    APIExceptionCode.PLAYER_ALREADY_JOINED,
                    http_code=status.HTTP_400_BAD_REQUEST
                )

        player_count = self.players.filter(time_withdrawn=None).count()
        if player_count >= Game.MAX_PLAYERS:
            raise APIException(
                'Max number of players (%s) reached' % Game.MAX_PLAYERS,
                APIExceptionCode.GAME_MAX_PLAYERS_REACHED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        if player and player.has_left():
            player.time_withdrawn = None
            player.save()
        else:
            player = self.players.create(
                user=user,
                team=Teams.VILLAGER.value,
                position=player_count + 1
            )

    def get_player(self, username):
        return self.players.get(user__username=username)

    def get_next_player(self, player):
        active_players = self.players.filter(time_withdrawn=None)
        player_position = active_players.aggregate(models.Max('position'))
        return active_players.get(
            position=(player.position + 1) % player_position['position__max']
        )

    def end(self):
        self.time_ended = datetime.now()
        self.save()

    def start(self):
        if self.has_started():
            raise APIException(
                'Game has already started',
                APIExceptionCode.GAME_ALREADY_STARTED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        if self.has_ended():
            raise APIException(
                'Unable to start game. Seems like the game has already ended',
                APIExceptionCode.GAME_ALREADY_ENDED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        players = list(self.players.filter(time_withdrawn=None).all())
        if len(players) < Game.MIN_PLAYERS:
            raise APIException(
                'Unable to start without the minimum number of players: %d' % (
                    Game.MAX_PLAYERS
                ),
                APIExceptionCode.GAME_INSUFFICIENT_PLAYERS,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        shuffle(players)

        team_allocation = self.get_team_allocation(len(players))
        teams = []

        for team, size in team_allocation.items():
            teams += [Teams(team)] * size
        shuffle(teams)

        grand_inquisitor = None
        for idx, player in enumerate(players):
            player.position = idx + 1
            player.team = teams[idx].value

            if player.position is 1:
                grand_inquisitor = player

            player.save()

        self.time_started = datetime.now()

        turn = self.turns.create(
            number=1,
            current_phase=Phases.INITIAL.value,
            grand_inquisitor=grand_inquisitor,
            current_player=grand_inquisitor
        )

        self.active_turn = turn
        self.save()

    @staticmethod
    def get_team_allocation(player_count):
        return {
            Teams.WEREWOLF.value: math.ceil(player_count / 2) - 1,
            Teams.VILLAGER.value: math.floor(player_count / 2) + 1
        }

class PlayerManager(models.Manager):
    def get_queryset(self):
        # Eagerly-load `User` data since we won't be using the `Player` model by
        # itself anyways
        return super(PlayerManager, self).get_queryset().select_related('user')


class Player(models.Model):
    # Override default manager
    objects = PlayerManager()

    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='players'
    )

    team = models.CharField(
        max_length=10,
        choices=Teams.choices(),
        default=Teams.VILLAGER.value
    )
    position = models.IntegerField(default=1)

    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='+'
    )

    time_created = models.DateTimeField(auto_now_add=True)
    time_withdrawn = models.DateTimeField(blank=True, null=True, default=None)

    def has_left(self):
        if not self.time_withdrawn:
            return False
        return True

    def leave_game(self):
        if self.has_left():
            raise APIException(
                'Player already left',
                APIExceptionCode.PLAYER_ALREADY_LEFT,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        if self.game.has_started():
            raise APIException(
                'Unable to leave game. Game has already started',
                APIExceptionCode.GAME_ALREADY_STARTED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        if self.game.has_ended():
            raise APIException(
                'Game has already ended',
                APIExceptionCode.GAME_ALREADY_ENDED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        self.time_withdrawn = datetime.now()
        self.save()


class Turn(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='turns'
    )
    number = models.IntegerField()
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
        grand_inquisitor = self.game.get_next_player(self.grand_inquisitor)
        new_turn = self.game.turns.create(
            number=self.number + 1,
            grand_inquisitor=grand_inquisitor,
            current_phase=Phases.DAY.value,
            current_player=grand_inquisitor
        )
        self.game.active_turn = new_turn
        self.game.save()

        return new_turn


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


class Vote(models.Model):
    turn = models.ForeignKey(
        Turn, on_delete=models.DO_NOTHING, related_name='votes'
    )
    player = models.ForeignKey(
        Player, on_delete=models.DO_NOTHING, related_name='votes'
    )
    hut = models.ForeignKey(
        'Hut', on_delete=models.DO_NOTHING, related_name='votes'
    )

    time_created = models.DateTimeField(auto_now_add=True)
    time_removed = models.DateTimeField(null=True, blank=True, default=None)


class Inquisition(models.Model):
    turn = models.ForeignKey(
        Turn, on_delete=models.DO_NOTHING, related_name='inquisitions'
    )
    resident = models.ForeignKey(
        'Resident', on_delete=models.DO_NOTHING, related_name='+'
    )
    position = models.IntegerField()

    time_created = models.DateTimeField(auto_now_add=True)
