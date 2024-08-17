from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestRoutes(TestCase):

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

    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        users_status = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        url = reverse('notes:list')
        for user, note_in_list in users_status:
            with self.subTest(user=user):
                response = user.get(url)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        names_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, arg in names_args:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=arg)
                response = self.client.get(url)
                self.assertIn('form', response.context_data)
                self.assertIsInstance(response.context_data['form'], NoteForm)
