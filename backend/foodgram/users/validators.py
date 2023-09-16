import re

from rest_framework import serializers


def validate_name(value):
    if value == 'me':
        raise serializers.ValidationError(
            "Это имя использовать запрещено!"
        )
    result = re.sub('[\w.\@\+\-\([а-яА-яёЁ]+)', '', value)
    result_set = set(result)
    if len(result_set) != 0:
        raise serializers.ValidationError(
            f'Недопустимые символы {result_set} в имени пользователя.'
        )
    return value
