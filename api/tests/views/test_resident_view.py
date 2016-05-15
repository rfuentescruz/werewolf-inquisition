from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

from rest_framework import status

from .. import GameTestHelper


class ResidentViewTest(TestCase):
    def setUp(self):
        self.request = RequestFactory()

    def test_get_resident(self):
        """
        Test that resident data can be retrieved
        """
        game = GameTestHelper.create_start_ready_game()

        resident = game.residents.first()

        client = Client()
        client.force_login(game.owner.user)
        response = client.get(
            '/api/games/%d/residents/%d/' % (game.id, resident.id)
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        self.assertEquals(resident.id, response.json()['id'])
        self.assertEquals(resident.role.role, response.json()['role'])

    def test_get_resident_other_game(self):
        """
        Test that other game owners cannot delete another game's resident
        """
        game1 = GameTestHelper.create_start_ready_game()
        game2 = GameTestHelper.create_start_ready_game()

        resident = game2.residents.first()

        client = Client()
        client.force_login(game1.owner.user)
        response = client.get(
            '/api/games/%d/residents/%d/' % (game1.id, resident.id)
        )

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_resident_owner(self):
        """
        Test that residents may be added to the game based on their roles
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        client = Client()
        client.force_login(game.owner.user)
        response = client.post(
            '/api/games/%d/residents/' % game.id,
            {'role': 'villager'}
        )

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        query = game.residents.filter(role__role='villager')
        self.assertEquals(1, query.count())

        resident = query.first()

        self.assertEquals(resident.id, response.json()['id'])
        self.assertEquals(resident.role.role, response.json()['role'])

    def test_add_resident_invalid_role(self):
        """
        Test that only valid roles may be added as residents
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        resident_count = game.residents.count()

        client = Client()
        client.force_login(game.owner.user)
        response = client.post(
            '/api/games/%d/residents/' % game.id,
            {'role': 'foobar'}
        )

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(resident_count, game.residents.count())

    def test_add_resident_non_owner(self):
        """
        Test that only game owners can add residents
        """
        game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )

        resident_count = game.residents.count()

        player = User.objects.create(username='player')
        game.join(player)

        client = Client()
        client.force_login(player)
        response = client.post(
            '/api/games/%d/residents/' % game.id,
            {'role': 'villager'}
        )

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(resident_count, game.residents.count())

    def test_add_resident_already_started(self):
        """
        Test that residents cannot be added after a game has started
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        resident_count = game.residents.count()

        client = Client()
        client.force_login(game.owner.user)
        response = client.post(
            '/api/games/%d/residents/' % game.id,
            {'role': 'villager'}
        )

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(resident_count, game.residents.count())

    def test_add_resident_already_ended(self):
        """
        Test that residents cannot be added after a game has ended
        """
        game = GameTestHelper.create_start_ready_game()
        game.end()

        resident_count = game.residents.count()

        client = Client()
        client.force_login(game.owner.user)
        response = client.post(
            '/api/games/%d/residents/' % game.id,
            {'role': 'villager'}
        )

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(resident_count, game.residents.count())

    def test_delete_resident(self):
        """
        Test that residents can be removed from a game
        """
        game = GameTestHelper.create_start_ready_game()

        resident_count = game.residents.count()
        resident = game.residents.first()

        client = Client()
        client.force_login(game.owner.user)
        response = client.delete(
            '/api/games/%d/residents/%d/' % (game.id, resident.id)
        )

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(resident_count - 1, game.residents.count())

    def test_delete_resident_game_already_started(self):
        """
        Test that residents cannot be removed after the game has started
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        resident_count = game.residents.count()
        resident = game.residents.first()

        client = Client()
        client.force_login(game.owner.user)
        response = client.delete(
            '/api/games/%d/residents/%d/' % (game.id, resident.id)
        )

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(resident_count, game.residents.count())

    def test_delete_resident_non_owner(self):
        """
        Test that residents can only be removed by the game owner
        """
        game = GameTestHelper.create_start_ready_game()

        resident_count = game.residents.count()
        resident = game.residents.first()

        player = User.objects.create(username='player')
        game.join(player)

        client = Client()
        client.force_login(player)
        response = client.delete(
            '/api/games/%d/residents/%d/' % (game.id, resident.id)
        )

        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(resident_count, game.residents.count())

    def test_delete_resident_other_game(self):
        """
        Test that other game owners cannot delete another game's resident
        """
        game1 = GameTestHelper.create_start_ready_game()
        game2 = GameTestHelper.create_start_ready_game()

        resident = game2.residents.first()

        client = Client()
        client.force_login(game1.owner.user)
        response = client.delete(
            '/api/games/%d/residents/%d/' % (game1.id, resident.id)
        )

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_resident_not_allowed(self):
        """
        Test that updating a resident is not allowed at all
        """
        game = GameTestHelper.create_start_ready_game()

        resident = game.residents.first()

        client = Client()
        client.force_login(game.owner.user)
        response = client.put(
            '/api/games/%d/residents/%d/' % (game.id, resident.id),
            {'role': 'werewolf'}
        )

        self.assertEquals(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )


class ResidentViewSetAuthTest(TestCase):
    def setUp(self):
        self.game = GameTestHelper.create_game(
            User.objects.create(username='owner')
        )
        self.owner = self.game.owner

    def get_test_data(self):
        return {
            ('/api/games/%d/residents/' % self.game.id): {},
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
