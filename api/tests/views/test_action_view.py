from django.test import Client, RequestFactory, TestCase

from rest_framework import status

from .. import GameTestHelper
from ...models import Roles


class ActionViewTest(TestCase):
    def setUp(self):
        self.request = RequestFactory()

    def test_duplicate_action(self):
        """
        Test that a resident's action cannot be used twice in a turn
        """

        game = GameTestHelper.create_start_ready_game(roles=[Roles.SEER])
        game.start()

        client = Client()
        client.force_login(game.owner.user)

        hut = game.huts.first()
        seer = game.residents.get(role__role=Roles.SEER.value)

        response = client.post(
            '/api/games/%d/actions/seer/' % game.id,
            {
                'resident': seer.id,
                'hut': hut.id
            }
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        response = client.post(
            '/api/games/%d/actions/seer/' % game.id,
            {
                'resident': seer.id,
                'hut': hut.id
            }
        )

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_villager_action(self):
        """
        Test that the Villager's action gives a player 2 votes
        """

        game = GameTestHelper.create_start_ready_game()
        game.start()

        client = Client()
        client.force_login(game.owner.user)

        hut = game.huts.first()
        villager = game.residents.filter(
            role__role=Roles.VILLAGER.value
        ).first()
        self.assertEquals(0, game.owner.votes.count())

        response = client.post(
            '/api/games/%d/actions/villager/' % game.id,
            {
                'resident': villager.id,
                'hut': hut.id
            }
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        self.assertEquals(2, game.owner.votes.count())
        self.assertEquals(1, hut.votes.count())

    def test_seer(self):
        """
        Test that the seer action can be completed successfully
        """
        game = GameTestHelper.create_start_ready_game(roles=[Roles.SEER])
        game.start()

        hut = game.huts.first()
        seer = game.residents.get(role__role=Roles.SEER.value)

        client = Client()
        client.force_login(game.owner.user)
        response = client.post(
            '/api/games/%d/actions/seer/' % game.id,
            {
                'resident': seer.id,
                'hut': hut.id
            }
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(1, game.active_turn.actions.count())

        action = game.active_turn.actions.get(player=game.owner)

        self.assertEquals(seer, action.resident)
        self.assertEquals(game.owner, action.player)
        self.assertEquals(hut, action.targets.first().hut)

    def test_seer_action_invalid_hut(self):
        """
        Test that the seer action can be completed successfully
        """
        game = GameTestHelper.create_start_ready_game(roles=[Roles.SEER])
        game.start()

        seer = game.residents.get(role__role=Roles.SEER.value)
        other_game = GameTestHelper.create_start_ready_game(
            roles=[Roles.SEER]
        )
        other_hut = other_game.huts.first()

        client = Client()
        client.force_login(game.owner.user)
        response = client.post(
            '/api/games/%d/actions/seer/' % game.id,
            {
                'resident': seer.id,
                'hut': other_hut.id
            }
        )

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
