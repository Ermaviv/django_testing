from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest import lazy_fixture as lf
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import (FORM_DATA,
                                        NEW_FORM_DATA,
                                        )


@pytest.mark.parametrize(
    'user, expected_comments_count',
    (
        (lf('author_client'), 1),
        (lf('client'), 0)

    )
)
def test_user_try_create_comment(
        user,
        new,
        expected_comments_count,
        author,
        reverse_url
):
    comments_before = set(Comment.objects.all())
    user.post(reverse_url['detail'], FORM_DATA)
    comments_after = set(Comment.objects.all())
    current_comment = comments_after.difference(comments_before)
    assert current_comment.__len__() == expected_comments_count
    if expected_comments_count > 0:
        current_comment = current_comment.pop()
        assert current_comment.text == FORM_DATA['text']
        assert current_comment.author == author
        assert current_comment.news.pk == new.pk


def test_user_cant_use_bad_words(author_client, new):
    bad_words_data = {'text': f'Автор написал, {BAD_WORDS[0]}, и комментарий'}
    comment_count_before = Comment.objects.count()
    url = reverse('news:detail', args=(new.pk,))
    response = author_client.post(url, data=bad_words_data)
    comment_count_after = Comment.objects.count()
    assert comment_count_before == comment_count_after
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


@pytest.mark.parametrize(
    'user, expected_comment_count_change, expected_status',
    (
        (lf('not_author_client'), 0, HTTPStatus.NOT_FOUND),
        (lf('author_client'), 1, HTTPStatus.FOUND)
    )
)
def test_user_change_comment(
        user,
        comment,
        expected_comment_count_change,
        expected_status,
        new
):
    count_before = Comment.objects.count()
    url = reverse('news:delete', args=[comment.pk])
    url_to_comments = reverse('news:detail', args=(new.pk,)) + '#comments'
    response = user.post(url)
    if expected_comment_count_change == 1:
        assertRedirects(response, url_to_comments)
    assert response.status_code == expected_status
    count_after = Comment.objects.count()
    assert (count_before - count_after) == expected_comment_count_change


def test_author_can_edit_comment(author_client, comment, new, author):
    url = reverse('news:edit', args=(comment.pk,))
    url_to_comments = reverse('news:detail', args=(new.pk,)) + '#comments'
    response = author_client.post(url, data=NEW_FORM_DATA)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_FORM_DATA['text']
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment
):
    url = reverse('news:edit', args=(comment.pk,))
    response = not_author_client.post(url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.get(pk=comment.pk).news == comment.news
    assert Comment.objects.get(pk=comment.pk).author == comment.author
    assert Comment.objects.get(pk=comment.pk).text == comment.text
