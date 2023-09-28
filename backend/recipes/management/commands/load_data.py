import csv
from io import StringIO

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand, call_command, CommandError
from django.db import connection

from recipes.models import Ingredient


DATA = {
    Ingredient: 'ingredients.csv',
}

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            for model, csvfile in DATA.items():
                with open(
                    f'{settings.BASE_DIR}/data/{csvfile}',
                    'r', encoding='utf-8',
                ) as data:
                    reader = csv.DictReader(data)
                    model.objects.bulk_create(model(**row) for row in reader)
        except FileNotFoundError:
            raise CommandError(f'Файл {csvfile} не найден.')
        self.stdout.write(self.style.SUCCESS(
            'Данные загружены успешно.')
        )

        commands = StringIO()
        for app in apps.get_app_configs():
            call_command(
                'sqlsequencereset', app.label, stdout=commands, no_color=True
            )
        with connection.cursor() as cursor:
            cursor.execute(commands.getvalue())
