from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest import lazy_fixture as lf
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page(client, new, reverse_url):
    response = client.get(reverse_url['detail'])
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirection_edit_and_delete_comment(client, name, new):
    url = reverse(name, args=(new.pk,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name, parametrized_client, status',
    (
        ('news:edit', lf('not_author_client'), HTTPStatus.NOT_FOUND),
        ('news:edit', lf('author_client'), HTTPStatus.OK),
        ('news:delete', lf('not_author_client'), HTTPStatus.NOT_FOUND),
        ('news:delete', lf('author_client'), HTTPStatus.OK)

    ),
)
def test_author_outsider_change_comment(
        comment, name, parametrized_client, status
):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == status
