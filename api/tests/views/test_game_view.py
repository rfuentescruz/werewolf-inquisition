import json

from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from rest_framework import status

from .. import GameTestHelper
from ...models import Game


class GameViewTest(TestCase):
    def setUp(self):
        self.request = RequestFactory()

    def test_create(self):
        """
        Test that users can create games and become owners of it
        """
        user = User.objects.create(username='owner')

        client = Client()
        client.force_login(user)
        response = client.post('/api/games/')

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        game = Game.objects.get(pk=response.json()['id'])
        self.assertEquals(game.owner.user, user)
        self.assertEquals(game.players.first().user, user)

    def test_get_game_list(self):
        """
        Test that the game list should not contain related model data
        """
        game = GameTestHelper.create_start_ready_game()

        client = Client()
        client.force_login(game.owner.user)

        response = client.get('/api/games/')

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_json = response.json()

        for game_data in response_json:
            # These fields would require lots of JOINs for a game list
            self.assertNotIn('active_turn', game_data)
            self.assertNotIn('players', game_data)
            self.assertNotIn('residents', game_data)
            self.assertNotIn('residents', game_data)

    def test_get_game(self):
        """
        Test that game detail views should include model relationships
        """
        game = GameTestHelper.create_start_ready_game()

        client = Client()
        client.force_login(game.owner.user)

        response = client.get('/api/games/%d/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_json = response.json()

        self.assertIn('active_turn', response_json)
        self.assertIn('players', response_json)
        self.assertIn('residents', response_json)
        self.assertIn('residents', response_json)

    def test_update_winner(self):
        """
        Test that you can't actually update the winning team manually
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        user = User.objects.create(username='player')
        client = Client()
        client.force_login(user)

        response = client.put(
            '/api/games/%d/' % game.id,
            data=json.dumps({'winning_team': 'villager'}),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        game.refresh_from_db()
        self.assertIsNone(game.winning_team)

    def test_update_creation_time(self):
        """
        Test that you can't update the game creation time manually
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        original_creation_time = game.time_created

        client = Client()
        client.force_login(game.owner.user)

        response = client.put(
            '/api/games/%d/' % game.id,
            data=json.dumps({'time_created': datetime.now().isoformat()}),
            content_type='application/json'
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        game.refresh_from_db()
        self.assertEquals(game.time_created, original_creation_time)

    def test_update_start_time(self):
        """
        Test that you can't update the game start time manually
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        client = Client()
        client.force_login(game.owner.user)

        response = client.put(
            '/api/games/%d/' % game.id,
            data=json.dumps({'time_started': datetime.now().isoformat()}),
            content_type='application/json'
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        game.refresh_from_db()
        self.assertIsNone(game.time_started)

    def test_update_end_time(self):
        """
        Test that you can't update the game end time manually
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        client = Client()
        client.force_login(game.owner.user)

        response = client.put(
            '/api/games/%d/' % game.id,
            data=json.dumps({'time_ended': datetime.now().isoformat()}),
            content_type='application/json'
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        game.refresh_from_db()
        self.assertIsNone(game.time_ended)

    def test_update_active_turn(self):
        """
        Test that you can't change the current active turn manually
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        client = Client()
        client.force_login(game.owner.user)

        response = client.put(
            '/api/games/%d/' % game.id,
            data=json.dumps({'active_turn': 1}),
            content_type='application/json'
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        game.refresh_from_db()
        self.assertIsNone(game.active_turn)

    @patch('api.models.Game.join')
    def test_join(self, join):
        """
        Test that players can join a game
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        user = User.objects.create(username='player')
        client = Client()
        client.force_login(user)

        response = client.post('/api/games/%d/join/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(join.called_with(user))

    @patch('api.models.Player.leave_game')
    def test_leave_non_participant(self, leave):
        """
        Test that only players who have already joined the game can leave
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        user = User.objects.create(username='player')
        client = Client()
        client.force_login(user)

        response = client.post('/api/games/%d/leave/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(leave.called)

    @patch('api.models.Player.leave_game')
    def test_leave(self, leave):
        """
        Test that players can leave a game
        """
        user = User.objects.create(username='player')
        game = GameTestHelper.create_game(
            User.objects.create(username='owner'),
            players=[user]
        )

        client = Client()
        client.force_login(user)

        response = client.post('/api/games/%d/leave/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(leave.called)

    @patch('api.models.Game.start')
    def test_start_non_owner(self, start):
        """
        Test that games can only be started by its owner
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        user = User.objects.create(username='player')
        client = Client()
        client.force_login(user)

        response = client.post('/api/games/%d/start/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(start.called)

    @patch('api.models.Game.start')
    def test_start(self, start):
        """
        Test that games can be started by its owner successfully
        """
        user = User.objects.create(username='owner')
        game = GameTestHelper.create_game(user)

        client = Client()
        client.force_login(user)

        response = client.post('/api/games/%d/start/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(start.called)

    @patch('api.models.Game.end')
    def test_end_non_owner(self, end):
        """
        Test that games can only be ended by its owner
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        user = User.objects.create(username='player')
        client = Client()
        client.force_login(user)

        response = client.delete('/api/games/%d/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(end.called)

    @patch('api.models.Game.end')
    def test_end_already_started(self, end):
        """
        Test that games cannot be deleted once started
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        client = Client()
        client.force_login(game.owner.user)

        response = client.delete('/api/games/%d/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(end.called)

    @patch('api.models.Game.end')
    def test_end(self, end):
        """
        Test that games can be ended by its owner successfully
        """
        game = GameTestHelper.create_start_ready_game()

        client = Client()
        client.force_login(game.owner.user)

        response = client.delete('/api/games/%d/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(end.called)


class GameViewSetAuthTest(TestCase):
    def setUp(self):
        self.game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

    def get_test_data(self):
        return {
            '/api/games/': {},
            ('/api/games/%d/' % self.game.id): {},
            ('/api/games/%d/join/' % self.game.id): {},
            ('/api/games/%d/leave/' % self.game.id): {},
            ('/api/games/%d/start/' % self.game.id): {},
        }

    def test_make_unauthenticated_requests(self):
        """
        Test that the following routes do not accept unauthenticated requests
        """
        c = Client()

        for uri, data in self.get_test_data().items():
            response = c.post(uri, data=data)

            self.assertEquals(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                '%s did not return 403' % uri
            )
