from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import authentication
from rest_framework.authentication import get_authorization_header

from commons.jwt import JwtSecretKey


class AnonymousUser:
    id = None
    pk = None
    username = ''
    is_staff = False
    is_active = False
    is_superuser = False

    def __str__(self):
        return 'AnonymousUser'

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return 1  # instances always return the same hash value

    def __int__(self):
        raise TypeError('Cannot cast AnonymousUser to int. Are you trying to use it in place of User?')

    def save(self):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

    def delete(self):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

    def set_password(self, raw_password):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

    def check_password(self, raw_password):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousUser.")

    @property
    def is_anonymous(self):
        return True

    @property
    def is_authenticated(self):
        return False

    def get_username(self):
        return self.username


class JwtAuthenticationClient:
    model = get_user_model()
    jwt = JwtSecretKey()
    scheme = b'bearer'
    token_expires_in = getattr(settings, 'JWT_EXPIRES_IN', 3600)
    identity_field = 'email'

    def get_queryset(self):
        """
        Returns the user queryset.
        """
        return self.model.objects.filter(is_active=True)

    def get_object(self, sub):
        """
        Returns the user based on identity field.
        """
        queryset = self.get_queryset()

        try:
            user = queryset.get(**{self.identity_field: sub})

        except self.model.DoesNotExist:
            return None

        else:
            return user

    def authenticate(self, request):
        """
        Returns the authenticated user using the `Authorization`
        header to get the user token through the django request.
        """
        try:
            scheme, token = get_authorization_header(request).split()
            token = token.decode('utf-8')

        except (ValueError, TypeError):
            return None

        if scheme.lower() != self.scheme:
            return None

        claims = self.jwt.verify(token)

        if not claims:
            return None

        user = self.get_object(claims['sub'])

        if not user:
            # refuse the authentication if the user cannot be found.
            return None

        # otherwise, return the authenticated user.
        return user, token

    def sign_in(self, identity, password):
        """
        Login with email and password.

        Params:
            email (str, required): Email to login.
            password (str, required): Password to login.
        """
        user = self.get_object(identity)

        if not user:
            return None

        if not user.check_password(password):
            return None

        token, payload = self.generate_token(user)

        return user, token, payload

    def generate_token(self, user):
        """
        Build jwt token for a provided user.
        """
        identity = getattr(user, self.identity_field)
        return self.jwt.generate(sub=identity, exp=self.token_expires_in)


authentication_client = JwtAuthenticationClient()


class JwtAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        """
        Uses firebase client to authenticate a
        user based on a request token.
        """
        return authentication_client.authenticate(request)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'WWW-Authenticate'
