from django.db import models

from .turn import Turn


class Inquisition(models.Model):
    turn = models.ForeignKey(
        Turn, on_delete=models.DO_NOTHING, related_name='inquisitions'
    )
    resident = models.ForeignKey(
        'Resident', on_delete=models.DO_NOTHING, related_name='+'
    )
    position = models.IntegerField()

    time_created = models.DateTimeField(auto_now_add=True)
