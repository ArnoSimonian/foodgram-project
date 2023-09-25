#import re

# from rest_framework import serializers
from rest_framework.exceptions import ValidationError


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            "Имя пользователя 'me' использовать запрещено."
        )
    # result = re.sub('[\w.\@\+\-\([а-яА-яёЁ]+)', '', value)
    # result_set = set(result)
    # if len(result_set) != 0:
    #     raise serializers.ValidationError(
    #         f'Недопустимые символы {result_set} в имени пользователя.'
    #     )
    return value
