import re

from rest_framework.exceptions import ValidationError

from .constants import MAX_TAG_COLOR_LENGTH, TAG_COLOR_REGEX, TAG_NAME_REGEX

NOT_ALLOWED_TAG_NAME_CHAR_MSG = ("{chars} - недопустимые символы "
                                 "в названии тега {tag_name}.")
NOT_ALLOWED_TAG_COLOR_CHAR_MSG = ("{chars} - недопустимые символы "
                                  "в цвете тега {color} "
                                  "или цвет не начинается с символа '#'.")


def validate_tag_name(value):
    invalid_symbols = ''.join(set(re.sub(TAG_NAME_REGEX, '', value)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_TAG_NAME_CHAR_MSG.format(
                chars=invalid_symbols, tag_name=value
            )
        )
    return value


def validate_tag_color(value):
    invalid_symbols = ''.join(set(re.sub(TAG_COLOR_REGEX, '', value)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_TAG_COLOR_CHAR_MSG.format(
                chars=invalid_symbols, color=value
            )
        )
    if len(value) > MAX_TAG_COLOR_LENGTH:
        raise ValidationError(
            "Обозначение HEX-цвета не может быть длиннее 7 символов."
        )
    return value
