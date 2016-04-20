from django.test import TestCase

from .. import GameTestHelper

from ...models import Phases


class PlayerTest(TestCase):
    def test_end(self):
        """
        Test that ending a turn will create a new one
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        current_turn = game.active_turn
        new_turn = current_turn.end()

        self.assertEquals(game.active_turn, new_turn)
        self.assertEquals(new_turn.number, current_turn.number + 1)
        self.assertEquals(new_turn.current_phase, Phases.DAY.value)
        self.assertEquals(
            new_turn.grand_inquisitor.position,
            current_turn.grand_inquisitor.position + 1
        )
