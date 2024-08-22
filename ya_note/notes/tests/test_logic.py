from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


FORM_DATA = {
    'title': 'Новый заголовок',
    'text': 'Новый текст',
    'slug': 'new_slug'
}


class TestTemplateLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не_автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.url = reverse('notes:add')
        cls.url_done = reverse('notes:success')


class TestNotUniqueSlug(TestTemplateLogic):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок1',
            slug='slug',
            text='Текст заметки'
        )

    def test_not_unique_slug(self):
        notes_count_before = Note.objects.count()
        FORM_DATA['slug'] = self.note.slug
        response = self.author_client.post(self.url, data=FORM_DATA)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )


class TestCreateNote(TestTemplateLogic):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.client.post(self.url, data=FORM_DATA)
        notes_count_after = Note.objects.count()
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(notes_count_after, notes_count_before)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(self.url, data=FORM_DATA)
        self.assertRedirects(response, self.url_done)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, FORM_DATA['title'])
        self.assertEqual(new_note.text, FORM_DATA['text'])
        self.assertEqual(new_note.slug, FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)


class TestEditDeleteNote(TestNotUniqueSlug):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url_edit, FORM_DATA)
        self.assertRedirects(response, self.url_done)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, FORM_DATA['title'])
        self.assertEqual(self.note.text, FORM_DATA['text'])
        self.assertEqual(self.note.slug, FORM_DATA['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_other_user_cant_edit_note(self):
        response = self.not_author_client.post(self.url_edit, FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, self.author)

    def test_other_user_cant_delete_note(self):
        response = self.not_author_client.post(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.url_delete)
        self.assertRedirects(response, self.url_done)
        self.assertEqual(Note.objects.count(), 0)


class TestEmptySlug(TestTemplateLogic):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_empty_slug(self):
        Note.objects.all().delete()
        FORM_DATA.pop('slug')
        response = self.author_client.post(self.url, data=FORM_DATA)
        self.assertRedirects(response, self.url_done)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(FORM_DATA['title'])
        self.assertEqual(new_note.slug, expected_slug)
