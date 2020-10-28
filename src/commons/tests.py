import json

from django.conf import settings
from faker import Faker
from mixer.backend.django import mixer
from rest_framework import test

from commons.auth import authentication_client
from commons.schema import is_schema_valid


class APITestCase(test.APITestCase):
    # https://pypi.org/project/Faker/
    faker = Faker()

    def assertSchema(self, schema, data):
        """
        Check that data is valid for schema.
        """
        data, schema = dict(data), dict(schema)

        self.assertTrue(
            is_schema_valid(schema, data),
            f'\nThe Value: \n'
            f'{json.dumps(data, indent=2)} \n\n'
            f'Is not valid for schema: \n'
            f'{json.dumps(schema, indent=2)}'
        )

    def assertPaginatedSchema(self, schema, data):
        """
        Check that data is valid for schema.
        """
        schema = {
            'type': 'object',
            'properties': {
                'count': {'type': 'integer'},
                'next': {'type': ['string', 'null'], 'format': 'uri'},
                'previous': {'type': ['string', 'null'], 'format': 'uri'},
                'results': {
                    'type': 'array',
                    'items': schema
                }
            },
            'required': ['count', 'next', 'previous', 'results'],
            'additionalProperties': False
        }

        self.assertSchema(schema, data)


class AuthenticatedAPITestCase(APITestCase):

    def setUp(self):
        # define a default user to be used on tests.
        self.user = mixer.blend(settings.AUTH_USER_MODEL)

        # set this user as the default authenticated user.
        self.authenticate(self.user)

    def authenticate(self, user):
        """ Set user bearer token to authorization header. """
        token, _ = authentication_client.generate_token(user)
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'

    def unauthenticated(self):
        """ Cleans client authorization header. """
        if 'HTTP_AUTHORIZATION' in self.client.defaults:
            del self.client.defaults['HTTP_AUTHORIZATION']
