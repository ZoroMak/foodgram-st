from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Ingredient, Recipe, RecipeIngredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    measurement_unit = serializers.CharField()

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source="recipe_ingredients", many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and obj.shopping_cart.filter(user=request.user).exists()
        )


class CreateShortIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ("id", "amount")

    def validate_id(self, id):
        try:
            Ingredient.objects.get(id=id)
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError(f"Ингредиента с id {id} не существует.")

        return id

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Количество ингредиента должно быть больше {}!".format(0)
            )
        return value


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = CreateShortIngredientsSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return serializer.data

    def validate(self, data):
        ingredients = data.get("ingredients")
        cooking_time = data.get("cooking_time")
        image = data.get("image")

        if image is None:
            raise serializers.ValidationError(
                {"image": "Изображение является обязательным полем."}
            )

        if not ingredients:
            raise serializers.ValidationError(
                "Список ингредиентов не может быть пустым!"
            )

        ingredients_ids = [ingredient["id"] for ingredient in ingredients]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError("Ингредиенты должны быть уникальными!")

        if cooking_time is not None and cooking_time < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть не меньше 1 минуты!"
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")

        user = self.context.get("request").user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()

        self.create_ingredients(validated_data.pop("ingredients"), instance)

        return super().update(instance, validated_data)

    def create_ingredients(self, ingredients, recipe):
        instances = [
            RecipeIngredient(
                ingredient_id=element["id"], recipe=recipe, amount=element["amount"]
            )
            for element in ingredients
        ]
        RecipeIngredient.objects.bulk_create(instances)
