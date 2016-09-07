from django.test import TestCase


from ... import GameTestHelper
from ....exceptions import APIException, APIExceptionCode
from ....models import Roles
from ....models.residents import Seer


class SeerTest(TestCase):
    def test_action_return_hut_resident(self):
        """
        Test that the Seer action will return the resident of the target hut
        """

        game = GameTestHelper.create_start_ready_game(roles=[Roles.SEER])
        game.start()

        seer = Seer.objects.filter(
            game=game, role__role=Roles.SEER.value
        ).first()

        villager = game.residents.filter(
            role__role=Roles.VILLAGER.value
        ).first()

        resident = seer.use_action(player=game.owner, target_hut=villager.hut)
        self.assertEquals(villager, resident)

    def test_action_mark_hut_as_visited(self):
        """
        Test that the Seer action will mark the target hut as visited
        """

        game = GameTestHelper.create_start_ready_game(roles=[Roles.SEER])
        game.start()

        seer = Seer.objects.filter(
            game=game, role__role=Roles.SEER.value
        ).first()

        villager = game.residents.filter(
            role__role=Roles.VILLAGER.value
        ).first()

        seer.use_action(player=game.owner, target_hut=villager.hut)
        self.assertTrue(villager.hut.is_visited)

    def test_action_already_visited_target(self):
        """
        Test that the Seer action can only target unvisited huts
        """

        game = GameTestHelper.create_start_ready_game(roles=[Roles.SEER])
        game.start()

        seer = Seer.objects.filter(
            game=game, role__role=Roles.SEER.value
        ).first()

        villager = game.residents.filter(
            role__role=Roles.VILLAGER.value
        ).first()
        villager.hut.is_visited = True

        with self.assertRaises(APIException) as ex:
            seer.use_action(player=game.owner, target_hut=villager.hut)

        self.assertEquals(
            ex.exception.code, APIExceptionCode.ACTION_INVALID_TARGET
        )

    def test_action_invalid_actor_model(self):
        """
        Test that Seer models with invalid roles can't perform the Seer action
        """

        game = GameTestHelper.create_start_ready_game(roles=[Roles.SEER])
        game.start()

        seer = Seer.objects.filter(
            game=game, role__role=Roles.VILLAGER.value
        ).first()

        villager = game.residents.filter(
            role__role=Roles.VILLAGER.value
        ).first()

        with self.assertRaises(APIException) as ex:
            seer.use_action(player=game.owner, target_hut=villager.hut)

        self.assertEquals(
            ex.exception.code, APIExceptionCode.ACTION_INVALID_ACTOR
        )
