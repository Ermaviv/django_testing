from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


FORM_DATA = {
    'title': 'Новый заголовок',
    'text': 'Новый текст',
    'slug': 'slug'
}


class TestRoutes1(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не_автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок1',
            slug='slug',
            text='Текст заметки'
        )

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        FORM_DATA['slug'] = self.note.slug
        response = self.author_client.post(url, data=FORM_DATA)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)


class TestRoutes2(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=FORM_DATA)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        response = self.author_client.post(url, data=FORM_DATA)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, FORM_DATA['title'])
        self.assertEqual(new_note.text, FORM_DATA['text'])
        self.assertEqual(new_note.slug, FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)


class TestRoutes3(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_empty_slug(self):
        url = reverse('notes:add')
        FORM_DATA.pop('slug')
        response = self.author_client.post(url, data=FORM_DATA)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(FORM_DATA['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestCase4(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не_автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок1',
            slug='slug',
            text='Текст заметки'
        )

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.author_client.post(url, FORM_DATA)
        # self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, FORM_DATA['title'])
        self.assertEqual(self.note.text, FORM_DATA['text'])
        self.assertEqual(self.note.slug, FORM_DATA['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.not_author_client.post(url, FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
