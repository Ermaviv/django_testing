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
    assert len(current_comment) == expected_comments_count
    if expected_comments_count:
        current_comment = current_comment.pop()
        assert current_comment.text == FORM_DATA['text']
        assert current_comment.author == author
        assert current_comment.news.pk == new.pk


def test_user_cant_use_bad_words(author_client, new, reverse_url):
    bad_words_data = {'text': f'Автор написал, {BAD_WORDS[0]}, и комментарий'}
    comment_count_before = Comment.objects.count()
    response = author_client.post(reverse_url['detail'], data=bad_words_data)
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
        new,
        reverse_url
):
    count_before = Comment.objects.count()
    url_to_comments = reverse_url['detail'] + '#comments'
    response = user.post(reverse_url['delete'])
    if expected_comment_count_change:
        assertRedirects(response, url_to_comments)
    assert response.status_code == expected_status
    count_after = Comment.objects.count()
    assert (count_before - count_after) == expected_comment_count_change


def test_author_can_edit_comment(author_client, comment, new, author, reverse_url):
    url_to_comments = reverse_url['detail'] + '#comments'
    response = author_client.post(reverse_url['edit'], data=NEW_FORM_DATA)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_FORM_DATA['text']
    assert comment.author == author
    assert comment.news == new


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, reverse_url
):
    response = not_author_client.post(reverse_url['edit'], data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    check_comment = Comment.objects.get(pk=comment.pk)
    assert check_comment.news == comment.news
    assert check_comment.author == comment.author
    assert check_comment.text == comment.text
