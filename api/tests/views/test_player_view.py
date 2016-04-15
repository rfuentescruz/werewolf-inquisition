import json

from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from rest_framework import status

from .. import GameTestHelper
from ...models.game import Game, Player, Teams

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

    def test_get_own_player(self):
        """
        Test that users should be able to fetch their own player data
        """
        game = GameTestHelper.create_game(User.objects.create(username='owner'))

        client = Client()
        client.force_login(game.owner.user)

        response = client.get(
            '/api/games/%d/players/%d/' % (game.id, game.owner.id)
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_json = response.json()

        self.assertEquals(response_json['id'], game.owner.id)
        self.assertEquals(response_json['user'], game.owner.user.username)

    def test_get_other_player(self):
        """
        Test that users in the same game can fetch other player's data
        """
        user = User.objects.create(username='player')
        game = GameTestHelper.create_game(
            owner=User.objects.create(username='owner'),
            players=[user]
        )

        client = Client()
        client.force_login(game.owner.user)

        player = game.players.get(user=user)

        response = client.get(
            '/api/games/%d/players/%d/' % (game.id, player.id)
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_json = response.json()

        self.assertEquals(response_json['id'], player.id)
        self.assertEquals(response_json['user'], user.username)

    def test_get_players(self):
        """
        Test that players can fetch a list of their co-players in the game
        """
        game = GameTestHelper.create_start_ready_game()

        client = Client()
        client.force_login(game.owner.user)

        response = client.get('/api/games/%d/players/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_json = response.json()

        player_data = [
            {
                'id': player.id,
                'user': player.user.username,
                'position': player.position
            } for player in game.players.all()
        ]

        self.assertEquals(player_data, response_json)

    def test_get_players_other_game(self):
        """
        Test that players cannot fetch player data for another game
        """
        game = GameTestHelper.create_game(User.objects.create(username='user1'))
        other_game = GameTestHelper.create_game(
            User.objects.create(username='user2')
        )

        client = Client()
        client.force_login(game.owner.user)

        response = client.get('/api/games/%d/players/' % other_game.id)

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_player_villager(self):
        """
        Test that villagers should not be able to see player team data
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        villager = game.players.filter(team=Teams.VILLAGER.value).first()

        client = Client()
        client.force_login(villager.user)

        response = client.get('/api/games/%d/players/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_json = response.json()

        for player_data in response_json:
            self.assertFalse('team' in player_data)

    def test_get_player_werewolf(self):
        """
        Test that werewolves should be able to see player team data
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        werewolf = game.players.filter(team=Teams.WEREWOLF.value).first()

        client = Client()
        client.force_login(werewolf.user)

        response = client.get('/api/games/%d/players/' % game.id)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_json = response.json()

        for player_data in response_json:
            self.assertTrue('team' in player_data)

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

