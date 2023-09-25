import pandas as pd

from django.conf import settings
from django.db import connection
from pathlib import Path

from recipes.models import Ingredient


# DATA_DIR = Path(settings.DATA_ROOT)


def load_data_from_csv(csv_file_path):
    # Загрузка данных из CSV файла в DataFrame
    df = pd.read_csv(csv_file_path)

    # Преобразование DataFrame в список словарей (каждая строка CSV - словарь)
    data = df.to_dict(orient='records')

    # Очистка таблицы в базе данных
    with connection.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE recipes_ingredient RESTART IDENTITY CASCADE')

    # Загрузка данных в базу данных
    for record in data:
        Ingredient.objects.create(**record)


if __name__ == "__main__":
    # Укажите путь к вашему файлу CSV
    csv_file_path = Path(settings.DATA_ROOT / 'ingredients.csv')

    # Проверяем существование файла
    if csv_file_path.exists():
        load_data_from_csv(csv_file_path)
        print("Данные успешно загружены в базу данных.")
    else:
        print("Файл CSV не найден. Пожалуйста, укажите правильный путь.")


# # Вызываем функцию с указанием пути к файлу CSV
# load_data_from_csv('DATA_DIR / ingredients.csv')
