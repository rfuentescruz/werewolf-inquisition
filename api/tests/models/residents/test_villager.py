from django.test import TestCase

from ... import GameTestHelper
from ....exceptions import APIException, APIExceptionCode
from ....models import Roles
from ....models.residents import Villager


class VillagerTest(TestCase):
    def test_action_add_player_vote(self):
        """
        Test that the Villager action will add one vote to the current player
        """

        game = GameTestHelper.create_start_ready_game()
        game.start()

        villager = Villager.objects.filter(
            game=game, role__role=Roles.VILLAGER.value
        ).first()
        self.assertEquals(game.owner.votes.count(), 0)

        hut = game.huts.first()
        villager.use_action(player=game.owner, targets=[hut])

        self.assertEquals(game.owner.votes.filter(hut__isnull=True).count(), 1)

    def test_action_add_hut_vote(self):
        """
        Test that the Villager action will add one vote to the target hut
        """

        game = GameTestHelper.create_start_ready_game()
        game.start()

        villager = Villager.objects.filter(
            game=game, role__role=Roles.VILLAGER.value
        ).first()

        self.assertEquals(game.owner.votes.count(), 0)

        hut = game.huts.first()
        villager.use_action(player=game.owner, targets=[hut])

        self.assertEquals(game.owner.votes.filter(hut=hut).count(), 1)

    def test_action_no_targets(self):
        """
        Test that the Villager action throws an error when no targets are given
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        villager = Villager.objects.filter(
            game=game, role__role=Roles.VILLAGER.value
        ).first()

        self.assertEquals(game.owner.votes.count(), 0)

        with self.assertRaises(APIException) as error:
            villager.use_action(player=game.owner, targets=[])

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.ACTION_INVALID_TARGET
        )

    def test_action_non_hut_targets(self):
        """
        Test that the Villager action throws an error when targets are not Huts
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        villager = Villager.objects.filter(
            game=game, role__role=Roles.VILLAGER.value
        ).first()

        self.assertEquals(game.owner.votes.count(), 0)

        non_hut_target = game.residents.first()
        with self.assertRaises(APIException) as error:
            villager.use_action(player=game.owner, targets=[non_hut_target])

        self.assertEquals(
            error.exception.code,
            APIExceptionCode.ACTION_INVALID_TARGET
        )
