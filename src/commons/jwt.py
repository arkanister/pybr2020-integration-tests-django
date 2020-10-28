import datetime
import jwt

from django.conf import settings


JWT_SECRET_KEY = getattr(settings, 'JWT_SECRET_KEY', None)


class JwtSecretKey:

    def __init__(self, secret_key=None, algorithm='HS256', issuer=None):
        self.secret_key = secret_key or JWT_SECRET_KEY

        assert self.secret_key is not None, (
            'The \'secret_key\' must be provided or \'JWT_SECRET_KEY\' should be defined on settings.'
        )

        self.algorithm = algorithm
        self.issuer = issuer

    def _build_payload(self, **kwargs):
        """
        Build jwt payload.
        """
        now = datetime.datetime.utcnow()
        kwargs.setdefault('iat', now)

        if self.issuer:
            kwargs['iss'] = self.issuer

        exp = kwargs.pop('exp')

        if exp:
            kwargs['exp'] = now + datetime.timedelta(seconds=exp)

        return kwargs

    def generate(self, sub, exp=None, **kwargs):
        """
        Generate a jwt token based on provided claims.

        Args:
            sub (dict, required): token claims.
            exp (int, optional): seconds to expire token.
            kwargs (dict, optional): extra payload data.
        """
        payload = self._build_payload(sub=sub, exp=exp, **kwargs)
        token = jwt.encode(payload.copy(), self.secret_key, self.algorithm).decode('utf-8')
        return token, payload

    def verify(self, token):
        """
        Verify if a jwt token is valid.

        Args:
            token (str, required): token to be validated.
        """
        try:
            claims = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

        except (jwt.DecodeError, jwt.ExpiredSignature, jwt.InvalidSignatureError):
            return None

        else:
            return claims

