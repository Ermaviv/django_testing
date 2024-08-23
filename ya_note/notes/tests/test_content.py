from django.contrib.auth import get_user
from django.urls import reverse

from notes.forms import NoteForm
from notes.tests.conftest import TestData


class TestContent(TestData):

    def test_note_not_in_list_for_another_user(self):
        for user, note_in_list in self.users_status:
            with self.subTest(user=get_user(user)):
                response = user.get(self.url_list)
                note_content = response.context['object_list']
                self.assertIs((self.note in note_content), note_in_list)

    def test_pages_contains_form(self):
        for name, arg in self.names_args:
            with self.subTest(name=name):
                url = reverse(name, args=arg)
                response = self.author_client.get(url)
                self.assertIn('form', response.context_data)
                self.assertIsInstance(response.context_data['form'], NoteForm)
