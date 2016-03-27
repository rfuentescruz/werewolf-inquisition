from django.contrib.auth.models import User

from ..models.game import Game, Player
from ..models.village import Resident

class GameTestHelper(object):
    @classmethod
    def create_game(cls, owner, players=None):
        game = Game.objects.create()
        player = Player(
            game=game,
            user=owner,
            position=1
        )
        player.save()

        game.owner = player
        game.save()

        if players and len(players):
            for user in players:
                game.players.create(user=user)

        return game

    @classmethod
    def create_start_ready_game(cls):
        users = [
            User.objects.create(username='user%d' % (i + 1))
            for i in range(Game.MIN_PLAYERS)
        ]

        game = cls.create_game(owner=users[0], players=users[1:])
        return game
