from django.contrib import admin
from django.contrib.admin import register

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart)


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username', 'author__email')

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorites.count()


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


@register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')


@register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_filter = ('user', 'recipe')


@register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_filter = ('user', 'recipe')
