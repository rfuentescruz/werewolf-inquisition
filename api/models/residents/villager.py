from rest_framework import status

from ...exceptions import APIException, APIExceptionCode
from ...models import Hut, Resident


class Villager(Resident):
    class Meta:
        proxy = True

    def use_action(self, player, targets):
        super(self.__class__, self).use_action(player=player)

        if len(targets) != 1 or not isinstance(targets[0], Hut):
            raise APIException(
                'Seers must target exactly one hut',
                APIExceptionCode.ACTION_INVALID_TARGET,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        target_hut = targets[0]

        player.votes.create(turn=self.game.active_turn)
        player.votes.create(turn=self.game.active_turn, hut=target_hut)
