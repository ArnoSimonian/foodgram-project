from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from users.models import Subscribe, User
from users.validators import validate_name
from users.utils import EMAIL_LENGTH, USERNAME_LENGTH


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password')

    def validate_username(self, value):
        return validate_name(value)


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email')
            )
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous or (request.user == obj):
            return False
        return request.user.subscriber.filter(subscribing=obj).exists()


# class MeSerializer(UserSerializer):
#     class Meta(UserSerializer.Meta):
#         read_only_fields = ('role',)
