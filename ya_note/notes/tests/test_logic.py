from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.conftest import TestData, FORM_DATA


class TestLogic(TestData):

    def test_not_unique_slug(self):
        notes_count_before = Note.objects.count()
        FORM_DATA['slug'] = self.note.slug
        response = self.author_client.post(self.url_add, data=FORM_DATA)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.client.post(self.url_add, data=FORM_DATA)
        notes_count_after = Note.objects.count()
        expected_url = f'{self.login_url}?next={self.url_add}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(notes_count_after, notes_count_before)

    def test_user_can_create_note(self):
        notes_count_before = Note.objects.count()
        Note.objects.all().delete()
        response = self.author_client.post(self.url_add, data=FORM_DATA)
        self.assertRedirects(response, self.url_done)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, FORM_DATA['title'])
        self.assertEqual(new_note.text, FORM_DATA['text'])
        self.assertEqual(new_note.slug, FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_empty_slug(self):
        notes_count_before = Note.objects.count()
        Note.objects.all().delete()
        FORM_DATA.pop('slug')
        response = self.author_client.post(self.url_add, data=FORM_DATA)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertRedirects(response, self.url_done)
        new_note = Note.objects.get()
        expected_slug = slugify(FORM_DATA['title'])
        self.assertEqual(new_note.slug, expected_slug)

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
        self.assertEqual(self.note.author, note_from_db.author)

    def test_other_user_cant_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.not_author_client.post(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.url_delete)
        self.assertRedirects(response, self.url_done)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after - notes_count_before, -1)
