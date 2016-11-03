from rest_framework import status

from ...exceptions import APIException, APIExceptionCode
from ...models import Resident, Roles, Hut


class Seer(Resident):
    class Meta:
        proxy = True

    def use_action(self, player, targets):
        super(self.__class__, self).use_action(player=player)

        if self.role.role != Roles.SEER.value:
            raise APIException(
                'Only Seers may perform this action',
                APIExceptionCode.ACTION_INVALID_ACTOR,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        if len(targets) != 1 or not isinstance(targets[0], Hut):
            raise APIException(
                'Seers must target exactly one hut',
                APIExceptionCode.ACTION_INVALID_TARGET,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        target_hut = targets[0]

        if target_hut.game != self.game:
            raise APIException(
                'Seers can only target huts of the current game!',
                APIExceptionCode.ACTION_INVALID_TARGET,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        if target_hut.is_visited:
            raise APIException(
                'Seers can only target visited huts',
                APIExceptionCode.ACTION_INVALID_TARGET,
                http_code=status.HTTP_400_BAD_REQUEST
            )

        self.action.targets.create(hut=target_hut)

        target_hut.is_visited = True
        target_hut.save()

        return target_hut.resident
