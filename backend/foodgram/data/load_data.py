import csv
import os
import sys

import django

sys.path.append('../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")
django.setup()


def load_all_data(func):

    from recipes.models import Ingredients

    func('ingredients.csv', Ingredients)
    print('\nИнгридиенты загружены\n')


@load_all_data
def load_table_from_csv(fname, model):
    from recipes.models import Ingredients
    file = open(fname, 'r', encoding='utf-8')
    reader = csv.DictReader(file, delimiter=',')
    for row in reader:
        Ingredients.objects.create(
            name=row['абрикосовое варенье'], measurement_unit=row['г'])
        print(f'{row}')
