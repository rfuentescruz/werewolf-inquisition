from django.db import models
from rest_framework import status

from .game import Game
from .role import Role

from ..exceptions import APIException, APIExceptionCode

class Resident(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.DO_NOTHING, related_name='residents'
    )
    role = models.ForeignKey(
        Role, on_delete=models.DO_NOTHING, related_name='+'
    )

    time_eliminated = models.DateTimeField(blank=True, null=True, default=None)


    def action(self, *args, **kwargs):
        if bool(self.time_eliminated):
           raise APIException(
                'Eliminated roles cannot perform any further actions',
                APIExceptionCode.ACTION_INVALID_ACTOR,
                http_code=status.HTTP_400_BAD_REQUEST
            )
