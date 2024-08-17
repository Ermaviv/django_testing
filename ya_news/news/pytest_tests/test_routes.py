import pytest

from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# Страница отдельной новости доступна анонимному пользователю
@pytest.mark.django_db
def test_detail_page(client, new_id):
    url = reverse('news:detail', args=new_id)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# Если анонимный пользователь пытается изменить/удалить комментарий -
# он перенаправляется на страницу авторизации
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirection_edit_and_delete_comment(client, name, new_id):
    url = reverse(name, args=new_id)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
@pytest.mark.parametrize(
    'user, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
def test_author_outsider_change_comment(
        author_client, comment_id, name, user, expected_status
):
    url = reverse(name, args=comment_id)
    response = user.get(url)
    assert response.status_code == expected_status
