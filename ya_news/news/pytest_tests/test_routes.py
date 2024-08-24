from http import HTTPStatus

import pytest
from pytest import lazy_fixture as lf
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    ('edit', 'delete')
)
def test_redirection_edit_and_delete_comment(client, name, new, reverse_url):
    url = reverse_url[name]
    login_url = reverse_url['login']
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name, parametrized_client, status',
    (
        ('edit', lf('not_author_client'), HTTPStatus.NOT_FOUND),
        ('edit', lf('author_client'), HTTPStatus.OK),
        ('delete', lf('not_author_client'), HTTPStatus.NOT_FOUND),
        ('delete', lf('author_client'), HTTPStatus.OK),
        ('home', lf('client'), HTTPStatus.OK),
        ('login', lf('client'), HTTPStatus.OK),
        ('logout', lf('client'), HTTPStatus.OK),
        ('signup', lf('client'), HTTPStatus.OK),
        ('detail', lf('client'), HTTPStatus.OK),
    )
)
def test_user_change_comment(
        name, parametrized_client, status, reverse_url
):
    url = reverse_url[name]
    response = parametrized_client.get(url)
    assert response.status_code == status
