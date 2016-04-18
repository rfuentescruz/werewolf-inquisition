from django.test import TestCase

from .. import GameTestHelper

from ...exceptions import APIException, APIExceptionCode


class PlayerTest(TestCase):
    def test_player_leave_game_started(self):
        """
        Test that a player cannot leave a game once it has started
        """
        game = GameTestHelper.create_start_ready_game()
        leaver = game.players.last()

        game.start()
        with self.assertRaises(APIException) as ex:
            leaver.leave_game()

        self.assertEquals(
            ex.exception.code, APIExceptionCode.GAME_ALREADY_STARTED
        )

    def test_player_leave_game_ended(self):
        """
        Test that a player cannot leave a game once it has already ended
        """
        game = GameTestHelper.create_start_ready_game()
        leaver = game.players.last()

        game.end()
        with self.assertRaises(APIException) as ex:
            leaver.leave_game()

        self.assertEquals(
            ex.exception.code, APIExceptionCode.GAME_ALREADY_ENDED
        )

    def test_leave_player_already_left(self):
        """
        Test that a player cannot leave a game once it has already ended
        """
        game = GameTestHelper.create_start_ready_game()
        leaver = game.players.last()

        leaver.leave_game()
        with self.assertRaises(APIException) as ex:
            leaver.leave_game()

        self.assertEquals(
            ex.exception.code, APIExceptionCode.PLAYER_ALREADY_LEFT
        )

    def test_leave_player(self):
        """
        Test that a player cannot leave a game once it has already ended
        """
        game = GameTestHelper.create_start_ready_game()
        player_count = game.players.filter(time_withdrawn=None).count()

        leaver = game.players.last()
        leaver.leave_game()

        self.assertTrue(leaver.has_left())
        self.assertEquals(
            game.players.filter(time_withdrawn=None).count(),
            player_count - 1
        )
