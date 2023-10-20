from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .constants import NAME_REGEX, TAG_COLOR_REGEX

NAME_ERROR_MSG = ("Поле {0} может содержать только русские и латинские буквы "
                  "и пробел.")
TAG_COLOR_ERROR_MSG = ("Поле {0} должно содержать латинские буквы 'a-f/A-F' "
                       "и/или цифры, начинаться с символа '#' и содержать "
                       "3 или 6 символов после '#'.")
NOT_ALLOWED_ME = ("Нельзя создать пользователя с "
                  "именем '{username}' - это имя запрещено.")


tag_color_validator = RegexValidator(
    regex=TAG_COLOR_REGEX,
    message=TAG_COLOR_ERROR_MSG.format('color'),
)

name_validator = RegexValidator(
    regex=NAME_REGEX,
    message=NAME_ERROR_MSG.format('name'),
)


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            NOT_ALLOWED_ME.format(username=value)
        )
    return value
