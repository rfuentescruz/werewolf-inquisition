from django.contrib.auth.models import User

from ..models import Game


class GameTestHelper(object):
    @classmethod
    def create_game(cls, owner, players=None):
        game = Game.objects.create()
        game.players.create(
            user=owner,
            is_owner=True,
            position=1
        )

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
