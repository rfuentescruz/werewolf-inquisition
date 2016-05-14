from django.contrib.auth.models import User

from ..models import Game, Roles


class GameTestHelper(object):
    user_id = 0

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
    def create_start_ready_game(cls, num_players=Game.MIN_PLAYERS):
        if not Game.MIN_PLAYERS <= num_players <= Game.MAX_PLAYERS:
            raise ValueError(
                'num_players must be between %d and %d. Currently %d' % (
                    Game.MIN_PLAYERS, Game.MAX_PLAYERS, num_players
                )
            )

        users = []

        for i in range(num_players):
            users.append(
                User.objects.create(username='user_%d' % cls.user_id)
            )
            cls.user_id += 1

        game = cls.create_game(owner=users[0], players=users[1:])

        for i in range(Game.RESIDENT_COUNT):
            game.add_resident(Roles.VILLAGER)

        return game
