from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from api.pagination import DefaultPagination
from api.permissions import IsAuthorOrReadOnly

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, RecipeIngredient
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeMinifiedSerializer,
    RecipeSerializer,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer

        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=("get",),
        permission_classes=(IsAuthenticatedOrReadOnly,),
        url_path="get-link",
        url_name="get-link",
    )
    def get_short_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        short_link = f"{request.get_host()}/recipes/{recipe.id}"

        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="shopping_cart",
    )
    def shopping_cart(self, request):
        qs = Recipe.objects.filter(shopping_cart__user=request.user)
        page = self.paginate_queryset(qs)
        serializer = RecipeMinifiedSerializer(
            page or qs, many=True, context={"request": request}
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        qs = (
            RecipeIngredient.objects.filter(recipe__shopping_cart__user=request.user)
            .values(
                name=F("ingredient__name"),
                unit=F("ingredient__measurement_unit"),
            )
            .annotate(total_amount=Sum("amount"))
            .order_by("name")
        )

        lines = [
            f"{item['name']} ({item['unit']}) — {item['total_amount']}\n" for item in qs
        ]
        content = "".join(lines)
        return Response(content, content_type="text/plain")

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="shopping_cart",
    )
    def shopping_cart_change(self, request, pk=None):
        if request.method == "POST":
            return self.add_to_shopping_cart(request, pk)
        return self.remove_from_shopping_cart(request, pk)

    @staticmethod
    def add_to_shopping_cart(request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if recipe.shopping_cart.filter(user=user).exists():
            return Response(
                {"errors": "Рецепт уже в корзине"}, status=status.HTTP_400_BAD_REQUEST
            )
        recipe.shopping_cart.create(user=user)
        data = RecipeMinifiedSerializer(recipe, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)

    @staticmethod
    def remove_from_shopping_cart(request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if not recipe.shopping_cart.filter(user=user).exists():
            return Response(
                {"errors": "Рецепта нет в корзине"}, status=status.HTTP_400_BAD_REQUEST
            )
        recipe.shopping_cart.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
    )
    def list_favorites(self, request):
        qs = Recipe.objects.filter(favorites__user=request.user)
        page = self.paginate_queryset(qs)
        serializer = RecipeMinifiedSerializer(
            page or qs, many=True, context={"request": request}
        )
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
    )
    def favorite(self, request, pk=None):
        if request.method == "POST":
            return self.add_to_favorite(request, pk)
        return self.remove_from_favorite(request, pk)

    @staticmethod
    def add_to_favorite(request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if recipe.favorites.filter(user=request.user).exists():
            return Response(
                {"errors": "Рецепт уже в избранном"}, status=status.HTTP_400_BAD_REQUEST
            )
        recipe.favorites.create(user=request.user)
        data = RecipeMinifiedSerializer(recipe, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)

    @staticmethod
    def remove_from_favorite(request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe.favorites.filter(user=request.user).exists():
            return Response(
                {"errors": "Рецепта нет в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe.favorites.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
