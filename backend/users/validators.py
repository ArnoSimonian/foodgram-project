import re

from rest_framework.exceptions import ValidationError

    
USERNAME_REGEX = r'[\w\.@+-]+'
NOT_ALLOWED_ME = ("Нельзя создать пользователя с "
                  "именем '{username}' - это имя запрещено.")
NOT_ALLOWED_NAME_CHAR_MSG = ("{chars} - недопустимые символы "
                             "в имени пользователя {username}.")

def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            NOT_ALLOWED_ME.format(username=value)
        )
    invalid_symbols = ''.join(set(re.sub(USERNAME_REGEX, '', value)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_NAME_CHAR_MSG.format(
                chars=invalid_symbols, username=value
            )
        )
    return value
