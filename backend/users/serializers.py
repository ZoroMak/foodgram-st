from django.contrib.auth.password_validation import validate_password
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(use_url=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user in obj.subscribers.all()
        return False


class UserResponseOnCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name")


class SetAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(use_url=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate(self, data):
        avatar = self.initial_data.get("avatar")
        if not avatar:
            raise serializers.ValidationError("Нельзя загрузить пустой аватар")

        return data


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
