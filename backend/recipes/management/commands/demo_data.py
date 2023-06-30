import csv
import os
import random
from itertools import cycle

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from faker import Faker
from recipes.models import Ingredient, Tag
from recipes.models import Recipe
from recipes.models import RecipeIngredient
from rest_framework.authtoken.models import Token
from users.models import User

fake = Faker(['ru_RU', ])

DATA_DIR = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Create demo data'

    def handle(self, *args, **options):

        def create_objects_from_csv(file_path, create_func):
            with open(file_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    create_func(*row)

        def create_ingredient(name, measurement_unit):
            Ingredient.objects.update_or_create(
                name=name, measurement_unit=measurement_unit)

        def create_tag(name, color, slug):
            Tag.objects.update_or_create(name=name, color=color, slug=slug)

        create_objects_from_csv(
            os.path.join(DATA_DIR, 'ingredients.csv'),
            create_ingredient
        )
        create_objects_from_csv(os.path.join(DATA_DIR, 'tags.csv'), create_tag)

        if not User.objects.filter(email__startswith='user').exists():
            all_ingredients = Ingredient.objects.all()
            all_tags = Tag.objects.all()
            PHOTO_PATH = os.path.join(DATA_DIR, 'photo')
            image_cycle = cycle(range(1, 9))

            for i in range(4):
                user, created = User.objects.update_or_create(
                    email=f'user{i}@example.com',
                    defaults={
                        'email': f'user{i}@example.com',
                        'username': f'User{i}',
                        'first_name': fake.first_name_male(),
                        'last_name': fake.last_name_male(),
                        'password': make_password('p@ssw0rd1'),
                    },
                )
                token, created = Token.objects.update_or_create(user=user)
                for j in range(2):
                    ingredients = [random.choice(all_ingredients) for _ in
                                   range(4)]
                    tags = [random.choice(all_tags) for _ in range(2)]

                    image_file_path = os.path.join(
                        PHOTO_PATH, f'{next(image_cycle)}.jpg')
                    with open(image_file_path, 'rb') as image_file:
                        recipe = Recipe.objects.create(
                            author=user,
                            name=fake.sentence(
                                nb_words=2, variable_nb_words=False),
                            text=fake.paragraph(
                                nb_sentences=5, variable_nb_sentences=False),
                            cooking_time=random.randint(20, 120),
                            image=ImageFile(image_file, name=f'{j + 1}.jpg'),
                        )
                        RecipeIngredient.objects.bulk_create(
                            [
                                RecipeIngredient(
                                    recipe=recipe,
                                    ingredient_id=ingredient.id,
                                    amount=random.randint(1, 100)
                                ) for ingredient in ingredients
                            ]
                        )
                        recipe.ingredients.set(ingredients)
                        recipe.tags.set(tags)
                        recipe.save()
        else:
            print("Demo users already exist. Skipping demo data creation.")

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
