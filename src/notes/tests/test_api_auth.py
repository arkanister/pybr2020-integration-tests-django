from django.conf import settings
from django.urls import reverse
from mixer.backend.django import mixer
from parameterized import parameterized
from rest_framework import status

from commons.random import generate_strong_password
from commons.tests import APITestCase


class AuthAPITestCase(APITestCase):

    token_result_schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["id", "name", "email"],
                "additionalProperties": False
            },
            "token": {"type": "string"},
            "token_expiration_date": {"type": "string", "format": "date-time"}
        },
        "required": ["user", "token", "token_expiration_date"],
        "additionalProperties": False
    }

    def test_should_sigh_up(self):
        password = generate_strong_password()
        api_url = reverse('api:auth-sign-up')

        response = self.client.post(api_url, data={
            'name': self.faker.name(),
            'email': self.faker.email(),
            'password': password,
            'password_confirm': password
        })

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertSchema(self.token_result_schema, response.json())

    @parameterized.expand([
        'small1', '',
        (None, )  # considering none as missing field
    ])
    def test_should_not_sigh_up_with_invalid_password(self, password):
        data = {
            'name': self.faker.name(),
            'email': self.faker.email(),
            'password': password,
            'password_confirm': password
        }

        api_url = reverse('api:auth-sign-up')

        response = self.client.post(api_url, data={
            key: val for key, val in data.items() if val is not None
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_not_sigh_up_with_mismatch_passwords(self):
        api_url = reverse('api:auth-sign-up')

        response = self.client.post(api_url, data={
            'name': self.faker.name(),
            'email': self.faker.email(),
            'password': generate_strong_password(),
            'password_confirm': generate_strong_password()
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @parameterized.expand([
        'invalid_email', '',
        (None, )  # considering none as missing field
    ])
    def test_should_not_sigh_up_with_invalid_email(self, email):
        password = generate_strong_password()
        api_url = reverse('api:auth-sign-up')

        data = {
            'name': self.faker.name(),
            'email': email,
            'password': password,
            'password_confirm': password
        }

        response = self.client.post(api_url, data={
            key: val for key, val in data.items() if val is not None
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_not_sigh_up_with_existing_email(self):
        user = mixer.blend(settings.AUTH_USER_MODEL)
        password = generate_strong_password()
        api_url = reverse('api:auth-sign-up')

        response = self.client.post(api_url, data={
            'name': self.faker.name(),
            'email': user.email,
            'password': password,
            'password_confirm': password
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @parameterized.expand([
        '',
        (None,)  # considering none as missing field
    ])
    def test_should_not_sigh_up_with_invalid_email(self, name):
        password = generate_strong_password()
        api_url = reverse('api:auth-sign-up')

        data = {
            'name': name,
            'email': self.faker.email(),
            'password': password,
            'password_confirm': password
        }

        response = self.client.post(api_url, data={
            key: val for key, val in data.items() if val is not None
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_sigh_in(self):
        password = generate_strong_password()
        user = mixer.blend(settings.AUTH_USER_MODEL)
        user.set_password(password)
        user.save()

        api_url = reverse('api:auth-sign-in')

        response = self.client.post(api_url, data={
            'email': user.email,
            'password': password
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertSchema(self.token_result_schema, response.json())

    def test_should_not_sign_in_with_invalid_credentials(self):
        api_url = reverse('api:auth-sign-in')

        response = self.client.post(api_url, data={
            'email': self.faker.email(),
            'password': generate_strong_password()
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
