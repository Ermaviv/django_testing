from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment
from news.pytest_tests.conftest import FORM_DATA, NEW_FORM_DATA
from news.forms import BAD_WORDS, WARNING
from news.pytest_tests.conftest import COMMENT_TEXT, NEW_COMMENT_TEXT


@pytest.mark.parametrize(
    'user, expected_comments_count',
    (
        (pytest.lazy_fixture('client'), 0),
        (pytest.lazy_fixture('author_client'), 1)
    )
)
@pytest.mark.django_db
def test_user_try_create_comment(user, new_id, expected_comments_count):
    url = reverse('news:detail', args=new_id)
    user.post(url, FORM_DATA)
    assert Comment.objects.count() == expected_comments_count


def test_user_cant_use_bad_words(author_client, new_id):
    bad_words_data = {'text': f'Автор написал, {BAD_WORDS[0]}, и комментарий'}
    url = reverse('news:detail', args=new_id)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'user, expected_comment_count_change, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), 0, HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), 1, HTTPStatus.FOUND)
    )
)
def test_user_change_comment(
        user,
        comment,
        expected_comment_count_change,
        expected_status,
        new_id
):
    count_before = Comment.objects.count()
    url = reverse('news:delete', args=[comment.pk])
    url_to_comments = reverse('news:detail', args=new_id) + '#comments'
    response = user.post(url)
    if user == 'not_author_client':
        assertRedirects(response, url_to_comments)
    assert response.status_code == expected_status
    count_after = Comment.objects.count()
    assert (count_before - count_after) == expected_comment_count_change


# @pytest.mark.skip
@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, new_id):
    url = reverse('news:edit', args=(comment.pk,))
    url_to_comments = reverse('news:detail', args=new_id) + '#comments'
    response = author_client.post(url, data=NEW_FORM_DATA)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment_id, comment
):
    url = reverse('news:edit', args=comment_id)
    response = not_author_client.post(url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
