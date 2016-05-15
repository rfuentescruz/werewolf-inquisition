from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Player


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


class IsGameOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        game = view.get_game()

        if request.user == game.owner.user:
            return True

        return False
