from django.conf import settings
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework import status

from commons.tests import AuthenticatedAPITestCase
from notes import models


class CategoryAPITestCase(AuthenticatedAPITestCase):
    note_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "content": {"type": ["string", "null"]},
            "category": {
                "type": ["object", "null"],
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                },
                "required": ["id", "name"],
                "additionalProperties": False
            },
            "archived": {"type": "boolean"},
            "created_at": {"type": "string", "format": "date-time"},
            "last_update": {"type": "string", "format": "date-time"}
        },
        "required": ["id", "title", "content", "category", "archived", "created_at", "last_update"],
        "additionalProperties": False
    }

    def test_should_create(self):
        api_url = reverse('api:notes-list')

        response = self.client.post(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph()
        })

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertSchema(self.note_schema, response.json())

    def test_should_create_with_category(self):
        category = mixer.blend('notes.Category')
        api_url = reverse('api:notes-list')

        response = self.client.post(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph(),
            'category': category.pk
        })

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        data = response.json()

        self.assertSchema(self.note_schema, data)
        self.assertIsNotNone(data['category'])
        self.assertEqual(category.pk, data['category']['id'])

    def test_should_not_create_if_category_is_not_valid(self):
        api_url = reverse('api:notes-list')

        response = self.client.post(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph(),
            'category': 999
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_not_create_if_title_is_missing(self):
        api_url = reverse('api:notes-list')

        response = self.client.post(api_url, data={
            'content': self.faker.paragraph()
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_not_create_if_not_authenticated(self):
        api_url = reverse('api:notes-list')

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.post(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph()
        })

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_list(self):
        mixer.cycle(10).blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-list')

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(10, data['count'])
        self.assertEqual(10, len(data['results']))

    def test_should_list_only_owned_notes(self):
        unknown_user = mixer.blend(settings.AUTH_USER_MODEL)

        ids = {obj.pk for obj in mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph)}
        mixer.cycle(5).blend('notes.Note', user=unknown_user, content=self.faker.paragraph)
        api_url = reverse('api:notes-list')

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(5, data['count'])
        self.assertEqual(5, len(data['results']))
        self.assertTrue([result['id'] in ids for result in data['results']])

    def test_should_not_list_if_not_authenticated(self):
        mixer.cycle(10).blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-list')

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_list_by_category(self):
        category1 = mixer.blend('notes.Category')
        category2 = mixer.blend('notes.Category')
        mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph, category=category1)
        mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph, category=category2)
        mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph, category=None)
        api_url = reverse('api:notes-list')

        response = self.client.get(api_url, data={
            'category': category1.pk
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(5, data['count'])
        self.assertEqual(5, len(data['results']))
        self.assertTrue(all([result['category']['id'] == category1.pk for result in data['results']]))

    def test_should_not_list_by_category_if_category_does_not_exist(self):
        mixer.cycle(10).blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-list')

        response = self.client.get(api_url, data={
            'category': 999
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(0, data['count'])
        self.assertEqual(0, len(data['results']))

    def test_should_not_list_by_category_if_category_is_not_valid(self):
        mixer.cycle(10).blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-list')

        response = self.client.get(api_url, data={
            'category': 'INVALID_CATEGORY'
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(0, data['count'])
        self.assertEqual(0, len(data['results']))

    def test_should_list_archived(self):
        mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph, archived=True)
        mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph, archived=False)
        api_url = reverse('api:notes-list')

        response = self.client.get(api_url, data={
            'archived': True
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(5, data['count'])
        self.assertEqual(5, len(data['results']))
        self.assertTrue(all([result['archived'] for result in data['results']]))

    def test_should_list_not_archived(self):
        mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph, archived=True)
        mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph, archived=False)
        api_url = reverse('api:notes-list')

        response = self.client.get(api_url, data={
            'archived': False
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(5, data['count'])
        self.assertEqual(5, len(data['results']))
        self.assertTrue(all([not result['archived'] for result in data['results']]))

    def test_should_not_list_archived_if_parameter_is_not_valid(self):
        mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph, archived=True)
        mixer.cycle(5).blend('notes.Note', user=self.user, content=self.faker.paragraph, archived=False)
        api_url = reverse('api:notes-list')

        response = self.client.get(api_url, data={
            'archived': 'INVALID_PARAMETER'
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(0, data['count'])
        self.assertEqual(0, len(data['results']))

    def test_should_retrieve(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[note.pk])

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertSchema(self.note_schema, data)
        self.assertEqual(note.pk, data['id'])

    def test_should_not_retrieve_if_does_not_exist(self):
        api_url = reverse('api:notes-detail', args=[999])

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_retrieve_if_not_owner(self):
        unknown_user = mixer.blend(settings.AUTH_USER_MODEL)
        unknown_note = mixer.blend('notes.Note', user=unknown_user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[unknown_note.pk])

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_retrieve_if_unauthenticated(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[note.pk])

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_update(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[note.pk])

        response = self.client.put(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph(),
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertSchema(self.note_schema, data)
        self.assertEqual(note.pk, data['id'])

    def test_should_update_with_category(self):
        category = mixer.blend('notes.Category')
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[note.pk])

        response = self.client.put(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph(),
            'category': category.pk
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertSchema(self.note_schema, data)
        self.assertIsNotNone(data['category'])
        self.assertEqual(category.pk, data['category']['id'])

    def test_should_not_update_if_category_is_not_valid(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[note.pk])

        response = self.client.put(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph(),
            'category': 999
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_not_update_if_title_is_missing(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[note.pk])

        response = self.client.put(api_url, data={
            'content': self.faker.paragraph()
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_not_update_if_does_not_exist(self):
        api_url = reverse('api:notes-detail', args=[999])

        response = self.client.put(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph()
        })

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_update_if_not_owner(self):
        unknown_user = mixer.blend(settings.AUTH_USER_MODEL)
        unknown_note = mixer.blend('notes.Note', user=unknown_user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[unknown_note.pk])

        response = self.client.put(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph()
        })

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_update_if_unauthenticated(self):
        category = mixer.blend('notes.Category', user=self.user)
        api_url = reverse('api:notes-detail', args=[category.pk])

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.put(api_url, data={
            'title': self.faker.sentence(),
            'content': self.faker.paragraph()
        })

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_delete(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[note.pk])

        response = self.client.delete(api_url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertFalse(models.Note.objects.filter(pk=note.pk).exists())

    def test_should_not_delete_if_does_not_exist(self):
        api_url = reverse('api:notes-detail', args=[999])

        response = self.client.delete(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_delete_if_not_owner(self):
        unknown_user = mixer.blend(settings.AUTH_USER_MODEL)
        unknown_note = mixer.blend('notes.Note', user=unknown_user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[unknown_note.pk])

        response = self.client.delete(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_delete_if_unauthenticated(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph)
        api_url = reverse('api:notes-detail', args=[note.pk])

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.delete(api_url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_archive(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph, archived=False)
        api_url = reverse('api:notes-archive', args=[note.pk])

        response = self.client.put(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()
        self.assertSchema(self.note_schema, data)
        self.assertTrue(data['archived'])

    def test_should_not_archive_if_already_archived(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph, archived=True)
        api_url = reverse('api:notes-archive', args=[note.pk])

        response = self.client.put(api_url)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_should_not_archive_if_does_not_exist(self):
        api_url = reverse('api:notes-archive', args=[999])

        response = self.client.put(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_archive_if_not_owner(self):
        unknown_user = mixer.blend(settings.AUTH_USER_MODEL)
        unknown_note = mixer.blend('notes.Note', user=unknown_user, content=self.faker.paragraph, archived=False)
        api_url = reverse('api:notes-archive', args=[unknown_note.pk])

        response = self.client.put(api_url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_should_not_archive_if_unauthenticated(self):
        note = mixer.blend('notes.Note', user=self.user, content=self.faker.paragraph, archived=True)
        api_url = reverse('api:notes-archive', args=[note.pk])

        # force client to unauthenticated state.
        self.unauthenticated()

        response = self.client.put(api_url)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
