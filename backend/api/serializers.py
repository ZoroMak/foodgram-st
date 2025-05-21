from rest_framework import serializers

from recipes.serializers import RecipeMinifiedSerializer
from users.models import User


class UserWithRecipesSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and obj in request.user.subscriptions.all())

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            queryset = queryset[:int(recipes_limit)]
        return RecipeMinifiedSerializer(queryset, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()
