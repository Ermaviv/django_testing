from django.urls import reverse
import pytest

from news.pytest_tests.conftest import NEWS_COUNT_ON_HOME_PAGE
from news.forms import CommentForm


@pytest.mark.django_db
def test_pagination(client, news_10):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


def test_anonymous_client_has_no_form(client, comment_id):
    url = reverse('news:detail', args=comment_id)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, comment_id):
    url = reverse('news:detail', args=comment_id)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comments_order(client, comment_id):
    url = reverse('news:detail', args=comment_id)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    # Собираем временные метки всех новостей.
    all_timestamps = [comment.created for comment in all_comments]
    # Сортируем временные метки, менять порядок сортировки не надо.
    sorted_timestamps = sorted(all_timestamps)
    # Проверяем, что временные метки отсортированы правильно.
    assert all_timestamps == sorted_timestamps


def test_news_order(client, news_10):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates
