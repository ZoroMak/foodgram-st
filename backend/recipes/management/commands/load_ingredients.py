import json
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from a JSON file'

    def handle(self, *args, **options):
        json_path = os.path.join(os.path.dirname(__file__),
                                 '../../../data/ingredients.json')
        json_path = os.path.abspath(json_path)

        try:
            with open(json_path, encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                Ingredient.objects.get_or_create(**item)

            self.stdout.write(self.style.SUCCESS(
                f'Successfully loaded {len(data)} ingredients.')
            )

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(
                f'File not found: {json_path}')
            )

        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Error loading ingredients: {e}')
            )
