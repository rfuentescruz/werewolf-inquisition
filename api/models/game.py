import math

from datetime import datetime
from random import shuffle

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status

from ..exceptions import APIException, APIExceptionCode

from .team import Teams
from .phase import Phases
from .role import Role


class Game(models.Model):
    MIN_PLAYERS = 3
    MAX_PLAYERS = 12
    RESIDENT_COUNT = 12

    winning_team = models.CharField(
        max_length=10, choices=Teams.choices(),
        blank=True, null=True, default=None
    )

    time_created = models.DateTimeField(auto_now_add=True)
    time_started = models.DateTimeField(blank=True, null=True, default=None)
    time_ended = models.DateTimeField(blank=True, null=True, default=None)

    @property
    def owner(self):
        return self.players.get(is_owner=True)

    @property
    def active_turn(self):
        # Were using `filter` and `first` instead of `get` since there are
        # games without any active turns yet (e.g. hasn't started)
        return self.turns.filter(is_active=True).first()

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
        except ObjectDoesNotExist:
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

        if self.residents.count() != Game.RESIDENT_COUNT:
            raise APIException(
                'Game does not have the correct number of residents',
                APIExceptionCode.GAME_INCORRECT_RESIDENT_COUNT,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        self.initialize_huts()
        grand_inquisitor = self.initialize_players(players)

        self.turns.create(
            number=1,
            current_phase=Phases.INITIAL.value,
            grand_inquisitor=grand_inquisitor,
            current_player=grand_inquisitor
        )

        self.time_started = datetime.now()
        self.save()

    def initialize_players(self, players=None):
        if players is None:
            players = list(self.players.filter(time_withdrawn=None).all())

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

        return grand_inquisitor

    def initialize_huts(self):
        hut_numbers = list(range(1, Game.RESIDENT_COUNT + 1))
        shuffle(hut_numbers)

        for hut in self.huts.all():
            hut.position = hut_numbers.pop()
            hut.save()

    def add_resident(self, role_data):
        role = Role.objects.get(role=role_data.value)

        role_count = self.residents.filter(role=role).count()

        if role.max_count is not None and role_count >= role.max_count:
            raise APIException(
                'You may only have up to %s %s residents' % (
                    role.max_count, role.name
                ),
                APIExceptionCode.GAME_MAX_RESIDENT_FOR_ROLE_REACHED,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        resident = self.residents.create(role=role)
        self.huts.create(
            position=0,
            resident=resident
        )
        return resident

    @staticmethod
    def get_team_allocation(player_count):
        return {
            Teams.WEREWOLF.value: math.ceil(player_count / 2) - 1,
            Teams.VILLAGER.value: math.floor(player_count / 2) + 1
        }
