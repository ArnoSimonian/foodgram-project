import re

from django.core.exceptions import ValidationError

from .constants import NAME_REGEX

NOT_ALLOWED_ME = ("Нельзя создать пользователя с "
                  "именем '{username}' - это имя запрещено.")
NOT_ALLOWED_FIRST_NAME_CHAR_MSG = ("{chars} - недопустимые символы "
                                   "в имени {first_name}.")
NOT_ALLOWED_LAST_NAME_CHAR_MSG = ("{chars} - недопустимые символы "
                                  "в фамилии {last_name}.")


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            NOT_ALLOWED_ME.format(username=value)
        )
    return value


def validate_first_name(value):
    invalid_symbols = ''.join(set(re.sub(NAME_REGEX, '', value)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_FIRST_NAME_CHAR_MSG.format(
                chars=invalid_symbols, first_name=value
            )
        )
    return value


def validate_last_name(value):
    invalid_symbols = ''.join(set(re.sub(NAME_REGEX, '', value)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_LAST_NAME_CHAR_MSG.format(
                chars=invalid_symbols, last_name=value
            )
        )
    return value


class MaxLengthPasswordValidator:

    def __init__(self, max_length=150):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                "Пароль должен содержать не более 150 символов.",
                code='password_too_long',
                params={'max_length': self.max_length},
            )

    def get_help_text(self):
        return "Пароль должен содержать не более 150 символов."
