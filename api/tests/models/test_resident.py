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
            resident.action()

        self.assertEquals(
            ex.exception.code,
            APIExceptionCode.ACTION_INVALID_ACTOR
        )

