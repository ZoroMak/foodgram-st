import django_filters
from django_filters import rest_framework as filters

from .models import Recipe, Ingredient


class IngredientFilter(filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="istartswith"
    )

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.NumberFilter(method='filter_favorites')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_shopping_cart'
    )

    def filter_favorites(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if value not in (0, 1):
            return queryset
        if value == 1:
            if not (user and user.is_authenticated):
                return queryset.none()
            return queryset.filter(favorites__user=user)
        if not (user and user.is_authenticated):
            return queryset
        return queryset.exclude(favorites__user=user)

    def filter_shopping_cart(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if value not in (0, 1):
            return queryset
        if value == 1:
            if not (user and user.is_authenticated):
                return queryset.none()
            return queryset.filter(shopping_cart__user=user)
        # value == 0
        if not (user and user.is_authenticated):
            return queryset
        return queryset.exclude(shopping_cart__user=user)

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )
