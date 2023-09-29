#from django.contrib.auth import get_user_model
#from djoser.serializers import UserCreateSerializer, UserSerializer
from djoser import serializers as djoser_serializers
from rest_framework import serializers
#from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from recipes.serializers import RecipeShortSerializer

from .models import Subscribe, User
from .validators import validate_username
#from .utils import EMAIL_LENGTH, USERNAME_LENGTH

# User = get_user_model()


class UserCreateSerializer(djoser_serializers.UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password')
        read_only_fields = ('id',)

    def validate_username(self, value):
        return validate_username(value)


class UserSerializer(djoser_serializers.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

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
        request = self.context['request']
        if request.user.is_anonymous or (request.user == obj):
            return False
        return request.user.subscriber.filter(subscribing=obj).exists()


class UserSubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'subscribing'),
                message="Нельзя подписаться на автора дважды."
            )
        ]

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit', 0)
        queryset = obj.recipes.all()
        if recipes_limit > 0:
            queryset = queryset[:recipes_limit]
        serializer = RecipeShortSerializer(queryset, many=True, read_only=True)
        return serializer.data

    def validate(self, data):
        if self.context['request'].method == 'POST' and (
            self.context['request'].user.pk == self.context['view'].kwargs.get(
                'user_id')
        ):
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя.')
        return data
