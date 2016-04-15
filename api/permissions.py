from rest_framework.permissions import BasePermission

from .models.game import Player


class IsGameParticipant(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True

        try:
            player = view.get_game().get_player(request.user.username)
        except Player.DoesNotExist:
            return False
        else:
            return not player.has_left()
