from django.http import Http404

from rest_framework import generics, status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import models
from .permissions import IsGameParticipant, IsGameOwnerOrReadOnly
from .serializers import (
    GameSerializer, PlayerSerializer, ResidentSerializer, TurnSerializer
)


class GameViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = GameSerializer
    queryset = models.Game.objects.all()

    def create(self, request):
        game = models.Game.objects.create()
        game.players.create(
            user=request.user,
            position=1,
            is_owner=True,
            team=models.Teams.VILLAGER.value
        )

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
        except models.Player.DoesNotExist:
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
    permission_classes = (IsAuthenticated, IsGameParticipant, )
    serializer_class = PlayerSerializer

    def get_queryset(self):
        game = self.get_game()
        return models.Player.objects.filter(game=game)

    def get_game(self):
        try:
            return models.Game.objects.get(pk=self.kwargs['game_id'])
        except models.Game.DoesNotExist:
            raise Http404

    def create(self, request, game_id):
        game = self.get_game()
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


class ResidentViewSet(viewsets.ViewSetMixin,
                      generics.ListCreateAPIView,
                      generics.RetrieveDestroyAPIView):
    permission_classes = (
        IsAuthenticated, IsGameParticipant, IsGameOwnerOrReadOnly
    )
    serializer_class = ResidentSerializer

    def get_queryset(self):
        game = self.get_game()
        return models.Resident.objects.filter(game=game)

    def get_game(self):
        try:
            return models.Game.objects.get(pk=self.kwargs['game_id'])
        except models.Game.DoesNotExist:
            raise Http404

    def create(self, request, game_id):
        game = self.get_game()

        if game.has_started() or game.has_ended():
            return Response(
                'Residents may not be modified after the game has started',
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            role = models.Roles(request.data['role'])
        except ValueError:
            return Response(
                'Invalid role provided "%s". Must be one of: %s' % (
                    request.data['role'], [r.value for r in models.Roles]
                ),
                status=status.HTTP_400_BAD_REQUEST
            )

        resident = game.add_resident(role)

        serializer = self.get_serializer(resident)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, game_id, pk):
        resident = self.get_object()

        if resident.game.has_started() or resident.game.has_ended():
            return Response(
                'Residents may not be modified after the game has started',
                status=status.HTTP_400_BAD_REQUEST
            )

        resident.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TurnViewSet(viewsets.ViewSetMixin,
                  generics.ListAPIView,
                  generics.RetrieveAPIView):

    permission_classes = (
        IsAuthenticated, IsGameParticipant, IsGameOwnerOrReadOnly
    )

    serializer_class = TurnSerializer

    def get_queryset(self):
        game = self.get_game()
        return models.Turn.objects.filter(game=game)

    def get_game(self):
        try:
            return models.Game.objects.get(pk=self.kwargs['game_id'])
        except models.Game.DoesNotExist:
            raise Http404
