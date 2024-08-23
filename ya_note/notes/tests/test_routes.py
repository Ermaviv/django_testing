from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.tests.conftest import TestData

User = get_user_model()


class TestRoutes(TestData):

    def test_availability_for_author(self):
        for name, args in self.urls_all:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        for name, args in self.urls_slug:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        for name, args in self.urls_all:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
