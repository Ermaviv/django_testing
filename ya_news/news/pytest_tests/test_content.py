from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from news.forms import CommentForm


def test_pagination(client, news, reverse_url):
    response = client.get(reverse_url['home'])
    news_count = response.context['object_list'].count()
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


def test_anonymous_client_has_no_form(client, new, reverse_url):
    response = client.get(reverse_url['detail'])
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, new, reverse_url):
    response = author_client.get(reverse_url['detail'])
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comments_order(client, new, reverse_url):
    response = client.get(reverse_url['detail'])
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_news_order(client, news, reverse_url):
    response = client.get(reverse_url['home'])
    all_dates = [
        news.date for news in response.context['object_list']
    ]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates
