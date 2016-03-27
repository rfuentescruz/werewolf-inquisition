from datetime import datetime
from random import shuffle

from django.contrib.auth.models import User

from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models.game import Game, Phases, Player, Teams
from .serializers import GameSerializer, PlayerSerializer


class GameViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = GameSerializer
    queryset = Game.objects.select_related('owner')


    def create(self, request):
        game = Game.objects.create()
        player = game.players.create(
            user=request.user,
            position=1,
            team=Teams.VILLAGER.value
        )
        game.owner = player
        game.save()

        serializer = self.get_serializer(game)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['POST'])
    def join(self, request, pk):
        game = self.get_object()
        game.join(request.user)

        serializer = self.get_serializer(game)
        return Response(serializer.data)

    @detail_route(methods=['POST'])
    def leave(self, request, pk):
        game = self.get_object()

        try:
            player = game.get_player(username=request.user.username)
        except Player.DoesNotExist:
            return Response(
                'You are not a participant of the game',
                status=status.HTTP_400_BAD_REQUEST
            )

        player.leave_game()

        return Response(None)

    @detail_route(methods=['POST'])
    def start(self, request, pk):
        game = self.get_object()

        if game.owner.user != request.user:
            return Response(
                "Unable to start game. You are not the game's owner",
                status=status.HTTP_403_FORBIDDEN
            )

        game.start()

        serializer = self.get_serializer(game)
        return Response(serializer.data)

    def destroy(self, request, pk):
        game = self.get_object()

        if game.owner.user != request.user:
            return Response(
                "Unable to delete game. You are not the game's owner",
                status=status.HTTP_403_FORBIDDEN
            )

        # Owners cannot unnaturally end game if it has already started
        if game.has_started():
            return Response(
                "Unable to delete game. Game has already started",
                status=status.HTTP_400_BAD_REQUEST
            )

        game.end()

        return Response(None)


class PlayerViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = PlayerSerializer

    def get_queryset(self):
        return Player.objects.filter(game=self.kwargs['game_id'])

    def create(self, request, game_id):
        try:
            game = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            return Response(
                'Game does not exist',
                status=status.HTTP_404_NOT_FOUND
            )

        player = game.join(request.user)

        serializer = self.get_serializer(player)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, game_id, pk):
        player = self.get_object()

        if player.user != request.user:
            return Response(
                'You may only remove yourself from the game.',
                status=status.HTTP_403_FORBIDDEN
            )

        player.leave_game()

        return Response(None)
