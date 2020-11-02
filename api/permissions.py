from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .exceptions import APIException, APIExceptionCode
from .models import Game, Player


class IsGameParticipant(BasePermission):
    def has_permission(self, request, view):
        try:
            game = get_object_or_404(Game, pk=view.kwargs['game_id'])
            player = game.get_player(request.user.username)
        except Player.DoesNotExist:
            return False
        except KeyError:
            raise APIException(
                'Game ID was not provided to the handler (view)',
                APIExceptionCodes.VIEW_MISSING_GAME_ID,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        else:
            return not player.has_left()


class IsGameOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        try:
            game = get_object_or_404(Game, pk=view.kwargs['game_id'])
        except KeyError:
            raise APIException(
                'Game ID was not provided to the handler (view)',
                APIExceptionCodes.VIEW_MISSING_GAME_ID,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if request.user == game.owner.user:
            return True

        return False
