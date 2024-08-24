from http import HTTPStatus

from notes.tests.conftest import TestData


class TestRoutes(TestData):

    def test_availability_for_author(self):
        for url in self.urls_all:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        for url in self.urls_slug:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        for url in self.urls_all:
            with self.subTest(url=url):
                expected_url = f'{self.url_login}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
