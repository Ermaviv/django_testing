from datetime import datetime, timedelta
import pytest
from django.test.client import Client

from news.models import News, Comment


NEWS_COUNT_ON_HOME_PAGE = 10
COMMENT_COUNT_ON_HOME_NEW = 2
FORM_DATA = {'text': 'Текст комментария'}
NEW_FORM_DATA = {'text': 'Обновлённый комментарий'}
COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
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
def new_id(new):
    return (new.pk,)


@pytest.fixture
def comment(author, new):
    return Comment.objects.create(
        news=new,
        author=author,
        text='Текст комментария',
        created=datetime.today(),
    )


@pytest.fixture
def comment_id(comment):
    return (comment.pk,)


@pytest.fixture
def comments(new, author):
    return Comment.objects.bulk_create(
        [
            Comment(
                news=new,
                author=author,
                text=f'Комментарий {index}',
                created=datetime.today() - timedelta(days=index),
            )
            for index in range(COMMENT_COUNT_ON_HOME_NEW)
        ]
    )


@pytest.fixture
def news_10(author):
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
