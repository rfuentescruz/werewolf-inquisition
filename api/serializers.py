from .models.game import Game, Player, Teams
from .models.village import Resident, Role, Hut

from rest_framework import serializers
from rest_framework.fields import SkipField


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def filter_fields(self, instance, fields):
        return fields

    def to_representation(self, instance):
        ret = {}
        fields = self.filter_fields(instance, self._readable_fields)

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            if attribute is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('name', 'role')


class PlayerSerializer(DynamicFieldsModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Player
        fields = ('id', 'user', 'position', 'team')
        read_only_fields = (
            'user',
            'team',
            'position',
        )
        depth = 2

    def filter_fields(self, instance, fields):
        is_werewolf_player = False
        if 'request' in self.context:
            try:
                player = instance.game.get_player(
                    self.context['request'].user.username
                )
            except Player.DoesNotExist:
                pass
            else:
                if player.team == Teams.WEREWOLF.value:
                    is_werewolf_player = True

        return [
            field for field in fields
            if field.field_name != 'team' or is_werewolf_player
        ]


class ResidentSerializer(serializers.ModelSerializer):
    role = RoleSerializer()
    class Meta:
        model = Resident
        fields = ('id', 'role', )
        depth = 2


class HutSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Hut
        fields = ('position', 'time_eliminated', 'resident', 'votes')
        read_only_fields = ('position', 'time_eliminated', 'resident', 'votes')


class GameSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.user.username')

    players = PlayerSerializer(
        read_only=True,
        many=True,
        fields=('id', 'user', 'position')
    )
    residents = ResidentSerializer(read_only=True, many=True)
    huts = HutSerializer(
        read_only=True,
        many=True,
        fields=('id', 'position', 'time_eliminated', 'votes')
    )

    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = (
            'active_turn',
            'winning_team',
            'time_created',
            'time_started',
            'time_ended'
        )
        depth = 1
