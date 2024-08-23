from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


COMMENT_COUNT_ON_HOME_NEW = 2
COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'
FORM_DATA = {'text': COMMENT_TEXT}
NEW_FORM_DATA = {'text': NEW_COMMENT_TEXT}


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def new():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=datetime.today(),
    )


@pytest.fixture
def comment(author, new):
    return Comment.objects.create(
        news=new,
        author=author,
        text='Текст комментария',
        created=datetime.today(),
    )


@pytest.fixture
def comments(new, author):
    for index in range(10):
        comment = Comment.objects.create(
            news=new, author=author, text=f'Tекст {index}',
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def news(author):
    return News.objects.bulk_create(
        [
            News(
                title=f'Заголовок {index}',
                text='Просто текст.',
                date=datetime.today() - timedelta(days=index)
            )
            for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    )


@pytest.fixture()
def reverse_url(new, comment):
    return {
        'home': reverse('news:home'),
        'login': reverse('users:login'),
        'logout': reverse('users:logout'),
        'signup': reverse('users:signup'),
        'detail': reverse('news:detail', args=(new.pk,)),
        'edit': reverse('news:edit', args=(comment.pk,)),
        'delete': reverse('news:delete', args=(comment.pk,))
    }
