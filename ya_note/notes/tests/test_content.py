from django.contrib.auth import get_user_model, get_user
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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
        cls.url = reverse('notes:list')
        cls.names_args = (
            ('notes:add', None),
            ('notes:edit', (cls.note.slug,))
        )

    def test_note_not_in_list_for_another_user(self):
        users_status = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for user, note_in_list in users_status:
            with self.subTest(user=get_user(user)):
                response = user.get(self.url)
                note_content = response.context['object_list']
                self.assertIs((self.note in note_content), note_in_list)

    def test_pages_contains_form(self):
        for name, arg in self.names_args:
            with self.subTest(name=name):
                url = reverse(name, args=arg)
                response = self.author_client.get(url)
                self.assertIn('form', response.context_data)
                self.assertIsInstance(response.context_data['form'], NoteForm)
