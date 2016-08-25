from datetime import datetime

from django.test import TestCase

from .. import GameTestHelper

from ...exceptions import APIException, APIExceptionCode
from ...models import Resident, Role, Roles


class ResidentTest(TestCase):
    def test_action_for_eliminated_residents(self):
        """
        Test that eliminated residents cannot perform any actions
        """
        game = GameTestHelper.create_game()
        role = Role.objects.filter(role=Roles.VILLAGER.value).first()

        resident = Resident.objects.create(game=game, role=role)
        resident.time_eliminated = datetime.now()

        with self.assertRaises(APIException) as ex:
            resident.use_action(player=game.owner)

        self.assertEquals(
            ex.exception.code,
            APIExceptionCode.ACTION_INVALID_ACTOR
        )

    def test_action_player_already_used_different_action(self):
        """
        Test that players cannot perform two different actions in one turn
        """
        game = GameTestHelper.create_start_ready_game()
        game.start()

        villager = game.residents.filter(
            role__role=Roles.VILLAGER.value
        ).first()

        seer_role = Role.objects.filter(role=Roles.SEER.value).first()
        seer = Resident.objects.create(game=game, role=seer_role)

        villager.use_action(player=game.owner)

        with self.assertRaises(APIException) as ex:
            seer.use_action(player=game.owner)

        self.assertEquals(
            ex.exception.code,
            APIExceptionCode.ACTION_ACTOR_MULTIPLE_ACTION
        )

    def test_action_already_perfomed(self):
        """
        Test that actions cannot be used twice in one turn
        """

        game = GameTestHelper.create_start_ready_game()
        game.start()

        villager = game.residents.filter(
            role__role=Roles.VILLAGER.value
        ).first()
        villager.use_action(player=game.owner)

        with self.assertRaises(APIException) as ex:
            villager.use_action(player=game.players.last())

        self.assertEquals(
            ex.exception.code,
            APIExceptionCode.ACTION_ALREADY_USED
        )
