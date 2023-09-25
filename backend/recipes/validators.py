import re

from rest_framework.exceptions import ValidationError


TAG_COLOR_REGEX = r'^#[0-9a-fA-F]'
TAG_SLUG_REGEX = r'[-a-zA-Z0-9_]+'
NOT_ALLOWED_COLOR_CHAR_MSG = ('{chars} - недопустимые символы '
                              'в цвете тега {tag}.')
NOT_ALLOWED_SLUG_CHAR_MSG = ('{chars} - недопустимые символы '
                             'в слаге тега {tag}.')


def validate_tag_color(value):
    invalid_symbols = ''.join(set(re.sub(TAG_COLOR_REGEX, '', value)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_COLOR_CHAR_MSG.format(
                chars=invalid_symbols, tag=value
            )
        )
    return value


def validate_tag_slug(value):
    invalid_symbols = ''.join(set(re.sub(TAG_SLUG_REGEX, '', value)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_SLUG_CHAR_MSG.format(
                chars=invalid_symbols, tag=value
            )
        )
    return value
