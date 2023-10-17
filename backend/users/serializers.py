from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Subscribe, User


class UserSerializer(serializers.ModelSerializer):
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

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request.user.is_anonymous or (request.user == obj):
            return False
        return request.user.subscriber.filter(subscribing=obj).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'subscribing',)
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'subscribing',),
                message="Нельзя подписаться на автора дважды.",
            ),
        ]

    def validate(self, data):
        if self.context['request'].method == 'POST' and (
            self.context['request'].user == data['subscribing']
        ):
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя."
            )
        if not data['subscribing'] and (
            self.context['request'].method == 'DELETE'
        ):
            raise serializers.ValidationError(
                "Вы не были подписаны на этого автора."
            )
        return data
