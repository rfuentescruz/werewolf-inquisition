import json

from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from rest_framework import status

from .. import GameTestHelper
from ...models.game import Game, Player

class PlayerViewTest(TestCase):
    def setUp(self):
        self.request = RequestFactory()

    def test_create(self):
        """
        Test that players can be POST'ed and join the game
        """
        game = GameTestHelper.create_game(User.objects.create(username='owner'))

        user = User.objects.create(username='player')

        client = Client()
        client.force_login(user)
        response = client.post('/api/games/%d/players/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self.assertEquals(game.players.count(), 2)
        self.assertEquals(game.players.last().user, user)

    def test_create_player_non_existent_game(self):
        """
        Test that players cannot join non-existent games
        """
        user = User.objects.create(username='player')

        client = Client()
        client.force_login(user)
        response = client.post('/api/games/999/players/')

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('api.models.game.Player.leave_game')
    def test_delete(self, leave):
        """
        Test that DELETE'ing players will cause them to leave their game
        """
        user = User.objects.create(username='player')
        game = GameTestHelper.create_game(
            User.objects.create(username='owner'),
            players=[user]
        )

        client = Client()
        client.force_login(user)

        response = client.delete(
            '/api/games/%d/players/%d/' % (
                game.id, game.get_player(user.username).id
            )
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(leave.called)

    @patch('api.models.game.Player.leave_game')
    def test_delete_other_player(self, leave):
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

        response = client.delete(
            '/api/games/%d/players/%d/' % (game.id, game.owner.id)
        )

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(leave.called)

    @patch('api.models.game.Player.leave_game')
    def test_delete_player_non_existent_game(self, leave):
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

        response = client.delete(
            '/api/games/999/players/%d/' % (game.get_player(user.username).id)
        )

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(leave.called)


class PlayerViewSetAuthTest(TestCase):
    def setUp(self):
        self.game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

    def get_test_data(self):
        return {
            ('/api/games/%d/players/' % self.game.id): {},
            ('/api/games/%d/players/%d/' % (self.game.id, self.game.owner.id)): {},
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

