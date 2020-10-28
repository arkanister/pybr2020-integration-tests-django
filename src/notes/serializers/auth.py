from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from notes import models


class SignUpSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField()

    class Meta:
        model = models.User
        fields = [
            'name', 'email', 'password', 'password_confirm'
        ]

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        password = validated_data.get('password')
        password_confirm = validated_data.pop('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password': _('Passwords do not match.')
            })

        # validate password rules
        # https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
        validate_password(password)

        return validated_data

    def create(self, validated_data):
        return models.User.objects.create(**validated_data)


class SignInSerializer(serializers.Serializer):  # noqa
    email = serializers.EmailField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = [
            'id', 'name', 'email'
        ]


class TokenSerializer(serializers.Serializer):  # noqa
    user = UserSerializer(many=False)
    token = serializers.CharField()
    token_expiration_date = serializers.DateTimeField()
