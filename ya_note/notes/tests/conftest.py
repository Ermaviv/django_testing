from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

FORM_DATA = {
    'title': 'Новый заголовок',
    'text': 'Новый текст',
    'slug': 'new_slug'
}


class TestData(TestCase):

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
        cls.login_url = reverse('users:login')
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_list = reverse('notes:list')
        cls.names_args = (
            ('notes:add', None),
            ('notes:edit', (cls.note.slug,))
        )
        cls.url_add = reverse('notes:add')
        cls.url_done = reverse('notes:success')
        cls.users_status = (
            (cls.author_client, True),
            (cls.not_author_client, False),
        )
        cls.urls_all = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        )
        cls.urls_slug = (
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        )
        cls.login_url = reverse('users:login')
