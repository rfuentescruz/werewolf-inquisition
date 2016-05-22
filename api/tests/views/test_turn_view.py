from django.test import RequestFactory, TestCase

from rest_framework import status

from .. import GameTestHelper
from ...models import Phases


class TurnViewTest(TestCase):
    def setUp(self):
        self.request = RequestFactory()

    def test_get_turn(self):
        """
        Test that you may get turn data from games
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        current_turn = game.active_turn

        self.client.force_login(game.owner.user)
        response = self.client.get(
            '/api/games/%d/turns/%d/' % (game.id, current_turn.id)
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertEquals(response_data['id'], current_turn.id)
        self.assertEquals(response_data['game'], current_turn.game.id)
        self.assertEquals(response_data['is_active'], current_turn.is_active)
        self.assertEquals(
            response_data['grand_inquisitor']['id'],
            current_turn.grand_inquisitor.id
        )
        self.assertEquals(
            response_data['current_player']['id'],
            current_turn.current_player.id
        )
        self.assertEquals(
            response_data['current_phase'],
            Phases(current_turn.current_phase).name
        )

    def test_get_turn_already_ended(self):
        """
        Test that you may get turn data from games even if they're ended
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        current_turn = game.active_turn
        current_turn.end()

        self.client.force_login(game.owner.user)
        response = self.client.get(
            '/api/games/%d/turns/%d/' % (game.id, current_turn.id)
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertEquals(response_data['id'], current_turn.id)
        self.assertEquals(response_data['game'], current_turn.game.id)
        self.assertEquals(response_data['is_active'], False)

    def test_list_turns(self):
        """
        Test that you may get a list of turns for the game
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        game.active_turn.end()

        self.client.force_login(game.owner.user)
        response = self.client.get(
            '/api/games/%d/turns/' % (game.id)
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        expected_turn_data = [
            {'id': t.id, 'is_active': t.is_active, 'game': t.game.id}
            for t in game.turns.all()
        ]

        actual_turn_data = [
            {'id': t['id'], 'is_active': t['is_active'], 'game': t['game']}
            for t in response_data
        ]

        self.assertCountEqual(expected_turn_data, actual_turn_data)

    def test_delete_turn(self):
        """
        Test that you may not delete a turn manually
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        current_turn = game.active_turn
        current_turn.end()

        self.client.force_login(game.owner.user)
        response = self.client.delete(
            '/api/games/%d/turns/%d/' % (game.id, current_turn.id)
        )
        self.assertEquals(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_create_turn(self):
        """
        Test that you may not create a turn manually
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        self.client.force_login(game.owner.user)
        response = self.client.post(
            '/api/games/%d/turns/' % (game.id),
            {'number': 2}
        )
        self.assertEquals(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_turn(self):
        """
        Test that you may not update a turn manually
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        self.client.force_login(game.owner.user)
        response = self.client.put(
            '/api/games/%d/turns/%d/' % (game.id, game.active_turn.id),
            {'number': 2}
        )

        self.assertEquals(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
