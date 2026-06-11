from django.test import TestCase
from django.urls import reverse


class GetCookieViewTestCase(TestCase):
    def test_get_cookie_view(self):
        response = self.client.get(reverse("myauth:cookie_get"))
        self.assertContains(response, "Cookie value")


class FoobarViewTestCase(TestCase):
    def test_foobar_view(self):
        response = self.client.get(reverse("myauth:foo-bar"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-type"], 'application/json'
        )
        expected_data = {"foo": "bar", "spam": "eggs"}
        self.assertEqual(response.json(), expected_data)