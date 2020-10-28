from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from commons.auth import authentication_client
from notes.serializers.auth import SignUpSerializer, TokenSerializer, SignInSerializer


class AuthViewSet(viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []

    @action(methods=['POST'], url_path='sign-up', detail=False)
    def sign_up(self, request):
        """
        Sign up user.
        """
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = serializer.save()
        token, payload = authentication_client.generate_token(obj)

        serializer = TokenSerializer({
            'user': obj,
            'token': token,
            'token_expiration_date': payload.get('exp')
        })

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], url_path='sign-in', detail=False)
    def sign_in(self, request):
        """
        Sign in with valid credentials.
        """
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = authentication_client.sign_in(
            identity=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        if not data:
            return Response(data={'email': [
                _('Unable to authenticate with provided credentials.')
            ]}, status=status.HTTP_400_BAD_REQUEST)

        user, token, payload = data

        serializer = TokenSerializer({
            'user': user,
            'token': token,
            'token_expiration_date': payload.get('exp')
        })

        return Response(data=serializer.data, status=status.HTTP_200_OK)