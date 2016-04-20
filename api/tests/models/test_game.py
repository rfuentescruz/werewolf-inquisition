from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from .. import GameTestHelper

from ...exceptions import APIException, APIExceptionCode
from ...models import Game, Phases, Player, Teams


class GameTest(TestCase):
    def test_join_with_maximum_players(self):
        """
        Test that users cannot join game once max players has been reached
        """
        players = []

        for i in range(Game.MAX_PLAYERS):
            players.append(User.objects.create(username='user%d' % i))

        game = GameTestHelper.create_game(
            owner=players[0], players=players[1:]
        )

        with self.assertRaises(APIException) as error:
            game.join(User.objects.create(username='other_user'))

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.GAME_MAX_PLAYERS_REACHED
        )

    def test_join_game_already_started(self):
        """"
        Test that users cannot join game once started
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        with self.assertRaises(APIException) as error:
            game.join(User.objects.create(username='other_user'))

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.GAME_ALREADY_STARTED
        )

    def test_join_game_already_ended(self):
        """
        Test that users cannot join game once ended
        """
        game = GameTestHelper.create_start_ready_game()
        game.end()

        with self.assertRaises(APIException) as error:
            game.join(User.objects.create(username='other_user'))

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.GAME_ALREADY_ENDED
        )

    def test_join(self):
        """
        Test that users can successfully join games
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        user = User.objects.create(username='player')
        game.join(user)

        self.assertEquals(game.players.count(), 2)
        self.assertEquals(game.get_player('player').user, user)

    def test_join_already_joined(self):
        """
        Test that users cannot join the same game twice (unless they left)
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        user = User.objects.create(username='player')
        game.join(user)

        with self.assertRaises(APIException) as error:
            game.join(user)

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.PLAYER_ALREADY_JOINED
        )

    def test_join_rejoin(self):
        """
        Test that users can rejoin games that they have left
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        user = User.objects.create(username='player')

        active_players = game.players.filter(time_withdrawn=None)

        game.join(user)
        self.assertEquals(active_players.count(), 2)

        player = game.get_player(username='player')
        player.leave_game()
        self.assertEquals(active_players.count(), 1)

        game.join(user)
        self.assertEquals(active_players.count(), 2)

    def test_rejoin_game_already_started(self):
        """
        Test that users cannot rejoin games once started
        """
        game = GameTestHelper.create_start_ready_game()

        player = game.players.last()
        player.leave_game()

        game.join(User.objects.create(username='other_user'))
        self.assertLess(game.players.count(), Game.MAX_PLAYERS)

        game.start()

        with self.assertRaises(APIException) as error:
            game.join(player.user)

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.GAME_ALREADY_STARTED
        )

    def test_rejoin_game_already_ended(self):
        """
        Test that users cannot rejoin games once ended
        """
        game = GameTestHelper.create_start_ready_game()

        player = game.players.last()
        player.leave_game()

        game.end()

        with self.assertRaises(APIException) as error:
            game.join(player.user)

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.GAME_ALREADY_ENDED
        )

    def test_rejoin_game_max_players(self):
        """
        Test that users cannot rejoin games if it has max no. of players
        """
        players = []

        for i in range(Game.MAX_PLAYERS):
            players.append(User.objects.create(username='user%d' % i))

        game = GameTestHelper.create_game(
            owner=players[0], players=players[1:]
        )

        leaver = game.players.last()
        leaver.leave_game()

        game.join(User.objects.create(username='other_user'))

        self.assertEquals(
            game.players.filter(time_withdrawn=None).count(),
            Game.MAX_PLAYERS
        )

        with self.assertRaises(APIException) as error:
            game.join(leaver.user)

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.GAME_MAX_PLAYERS_REACHED
        )

    def test_start_without_minimum_players(self):
        """
        Test that games cannot start without enough players
        """
        game = GameTestHelper.create_game(
            owner=User.objects.create(username='user')
        )

        self.assertLess(game.players.count(), Game.MIN_PLAYERS)

        with self.assertRaises(APIException) as error:
            game.start()

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.GAME_INSUFFICIENT_PLAYERS
        )

    def test_start_already_started(self):
        """
        Test that games that have already started cannot be started again
        """
        game = GameTestHelper.create_game(
            owner=User.objects.create(username='user')
        )
        game.time_started = datetime.now()

        with self.assertRaises(APIException) as error:
            game.start()

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.GAME_ALREADY_STARTED
        )

    def test_start_already_ended(self):
        """
        Test that games that have already ended cannot be started again
        """
        game = GameTestHelper.create_game(
            owner=User.objects.create(username='user')
        )
        game.time_ended = datetime.now()

        with self.assertRaises(APIException) as error:
            game.start()

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.GAME_ALREADY_ENDED
        )

    def test_start_allocate_player_position(self):
        """
        Test that player positions will be allocated and deduped on game start
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        self.assertEquals(game.players.count(), Game.MIN_PLAYERS)

        player_positions = sorted(
            [player.position for player in game.players.all()]
        )

        # By casting to a `set` we are de-duping player positions
        # and if there were duplicates the length will differ from the
        # length of the original list
        self.assertEquals(
            len(player_positions),
            len(set(player_positions))
        )

    def test_start_allocate_player_teams(self):
        """
        Test that players will be allocated to teams depending on game size
        """
        players = []

        for i in range(Game.MAX_PLAYERS):
            players.append(User.objects.create(username='user%d' % i))

        for size in range(Game.MIN_PLAYERS, Game.MAX_PLAYERS):
            game = GameTestHelper.create_game(
                owner=players[0],
                players=players[1:size]
            )
            game.start()

            team_counts = {}
            player_count = game.players.count()

            for player in game.players.all():
                if player.team not in team_counts:
                    team_counts[player.team] = 1
                else:
                    team_counts[player.team] += 1

            expected_team_counts = Game.get_team_allocation(player_count)
            self.assertEquals(team_counts, expected_team_counts)

    def test_start_active_turn(self):
        """
        Test that a new turn is created on game start
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        active_turn = game.active_turn

        self.assertEquals(active_turn.number, 1)
        self.assertEquals(active_turn.current_phase, Phases.INITIAL.value)
        self.assertEquals(active_turn.current_player.position, 1)
        self.assertEquals(
            active_turn.current_player,
            active_turn.grand_inquisitor
        )

    def test_get_team_allocation(self):
        expected_team_allocations = [
            # (size, (villager, werewolf))
            (3, (2, 1)),
            (4, (3, 1)),
            (5, (3, 2)),
            (6, (4, 2)),
            (7, (4, 3)),
            (8, (5, 3)),
            (9, (5, 4)),
            (10, (6, 4)),
            (11, (6, 5)),
            (12, (7, 5)),
        ]
        for size, allocation in expected_team_allocations:
            actual_allocation = Game.get_team_allocation(size)
            self.assertEquals(
                allocation[0], actual_allocation[Teams.VILLAGER.value]
            )
            self.assertEquals(
                allocation[1], actual_allocation[Teams.WEREWOLF.value]
            )

    def test_end_game_already_started(self):
        """
        Test that games can be ended after starting it
        """
        game = GameTestHelper.create_start_ready_game()

        game.start()
        self.assertTrue(game.has_started())

        game.end()
        self.assertTrue(game.has_ended())

    def test_end_game_not_started(self):
        """
        Test that games can be ended even if it hasn't started
        """
        game = GameTestHelper.create_start_ready_game()

        self.assertFalse(game.has_started())

        game.end()
        self.assertTrue(game.has_ended())

    def test_get_player(self):
        """
        Test that players data can be fetched via their usernames
        """
        player = User.objects.create(username='player')
        game = GameTestHelper.create_game(
            User.objects.create(username='owner'), players=[player]
        )

        self.assertEquals(game.get_player('player').user, player)

    def test_get_player_already_left(self):
        """
        Test that player data can be fetched from the game even after leaving
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner'),
            players=[
                User.objects.create(username='player')
            ]
        )

        player = game.get_player('player')
        player.leave_game()
        self.assertEquals(game.get_player('player'), player)

    def test_get_non_existent_player(self):
        """
        Test that player data can be fetched from the game even after leaving
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        with self.assertRaises(Player.DoesNotExist):
            game.get_player('player')

    def test_get_next_player(self):
        """
        Test that the 'next' player is the player one `position` higher
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        first_player = game.players.get(position=1)
        self.assertEquals(
            game.get_next_player(first_player),
            game.players.get(position=2)
        )

    def test_get_next_player_after_last_player(self):
        """
        Test that the 'next' player loops around the back to first player
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        last_player = game.players.get(position=game.players.count())
        self.assertEquals(
            game.get_next_player(last_player),
            game.players.get(position=1)
        )
