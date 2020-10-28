from django.conf import settings
from django.urls import reverse
from mixer.backend.django import mixer
from parameterized import parameterized
from rest_framework import status

from commons.tests import AuthenticatedAPITestCase
from notes import models


class CategoryAPITestCase(AuthenticatedAPITestCase):
    category_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["id", "name"],
        "additionalProperties": False
    }

    def test_should_create(self):
        api_url = reverse('api:categories-list')

        response = self.client.post(api_url, data={
            'name': self.faker.name()
        })

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertSchema(self.category_schema, response.json())

    @parameterized.expand(['', (None,)])
    def test_should_not_create_with_invalid_data(self, name):
        api_url = reverse('api:categories-list')

        data = {
            'name': name
        }

        response = self.client.post(api_url, data={k: v for k, v in data.items() if v is not None})

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_not_create_if_not_authenticated(self):
        api_url = reverse('api:categories-list')

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.post(api_url, data={
            'name': self.faker.name()
        })

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_list(self):
        mixer.cycle(20).blend('notes.Category', user=self.user)
        api_url = reverse('api:categories-list')

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.category_schema, data)
        self.assertEqual(20, data['count'])
        self.assertEqual(10, len(data['results']))

    def test_should_list_only_owned_categories(self):
        unknown_user = mixer.blend(settings.AUTH_USER_MODEL)

        ids = {obj.pk for obj in mixer.cycle(5).blend('notes.Category', user=self.user)}
        mixer.cycle(5).blend('notes.Category', user=unknown_user)

        api_url = reverse('api:categories-list')

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.category_schema, data)
        self.assertEqual(5, data['count'])
        self.assertEqual(5, len(data['results']))
        self.assertTrue(all(map(lambda x: x['id'] in ids, data['results'])))

    def test_should_not_list_if_unauthenticated(self):
        mixer.blend('notes.Category', user=self.user)
        api_url = reverse('api:categories-list')

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_retrieve(self):
        category = mixer.blend('notes.Category', user=self.user)
        api_url = reverse('api:categories-detail', args=[category.pk])

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertSchema(self.category_schema, data)
        self.assertEqual(category.pk, data['id'])

    def test_should_not_retrieve_if_does_not_exist(self):
        api_url = reverse('api:categories-detail', args=[999])

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_retrieve_if_not_owner(self):
        unknown_user = mixer.blend(settings.AUTH_USER_MODEL)
        unknown_category = mixer.blend('notes.Category', user=unknown_user)
        api_url = reverse('api:categories-detail', args=[unknown_category.pk])

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_retrieve_if_unauthenticated(self):
        category = mixer.blend('notes.Category', user=self.user)
        api_url = reverse('api:categories-detail', args=[category.pk])

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_update(self):
        category = mixer.blend('notes.Category', user=self.user)
        api_url = reverse('api:categories-detail', args=[category.pk])

        response = self.client.put(api_url, data={
            'name': self.faker.name()
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertSchema(self.category_schema, data)
        self.assertEqual(category.pk, data['id'])

    @parameterized.expand(['', (None,)])
    def test_should_not_update_with_invalid_data(self, name):
        category = mixer.blend('notes.Category', user=self.user)
        api_url = reverse('api:categories-detail', args=[category.pk])

        data = {
            'name': name
        }

        response = self.client.put(api_url, data={k: v for k, v in data.items() if v is not None})

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_not_update_if_does_not_exist(self):
        api_url = reverse('api:categories-detail', args=[999])

        response = self.client.put(api_url, data={
            'name': self.faker.name()
        })

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_update_if_not_owner(self):
        unknown_user = mixer.blend(settings.AUTH_USER_MODEL)
        unknown_category = mixer.blend('notes.Category', user=unknown_user)
        api_url = reverse('api:categories-detail', args=[unknown_category.pk])

        response = self.client.put(api_url, data={
            'name': self.faker.name()
        })

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_update_if_unauthenticated(self):
        category = mixer.blend('notes.Category', user=self.user)
        api_url = reverse('api:categories-detail', args=[category.pk])

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.put(api_url, data={
            'name': self.faker.name()
        })

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_delete(self):
        category = mixer.blend('notes.Category', user=self.user)
        api_url = reverse('api:categories-detail', args=[category.pk])

        response = self.client.delete(api_url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertFalse(models.Category.objects.filter(pk=category.pk).exists())

    def test_should_not_delete_if_does_not_exist(self):
        api_url = reverse('api:categories-detail', args=[999])

        response = self.client.delete(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_delete_if_not_owner(self):
        unknown_user = mixer.blend(settings.AUTH_USER_MODEL)
        unknown_category = mixer.blend('notes.Category', user=unknown_user)
        api_url = reverse('api:categories-detail', args=[unknown_category.pk])

        response = self.client.delete(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_delete_if_unauthenticated(self):
        category = mixer.blend('notes.Category', user=self.user)
        api_url = reverse('api:categories-detail', args=[category.pk])

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.delete(api_url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
