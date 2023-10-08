from djoser import serializers as djoser_serializers
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import User
from .validators import validate_username

# User = get_user_model()


class CustomUserCreateSerializer(djoser_serializers.UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)

    def validate_username(self, value):
        return validate_username(value)


class CustomUserSerializer(djoser_serializers.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email'),
                message="Пара 'username' и 'email' должна быть уникальной."
            )
        ]

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request.user.is_anonymous or (request.user == obj):
            return False
        return request.user.subscriber.filter(subscribing=obj).exists()
