from itertools import product
from random import choices
from string import ascii_letters

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order
from .utils import add_two_numbers


class AddTwoNumbersTest(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename="add_product")
        )
        self.client.login(username="testuser", password="testpass")

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": "Table",
                "price": "1234.45",
                "description": "GOOOD",
                "discount": "14",
            }
        )
        self.assertRedirects(response, reverse("shopapp:product_list"))


class ProductDetailViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username="testuser", password="testpass")
        cls.user = User.objects.create_user(**cls.credentials)
        cls.product = Product.objects.create(
            name="".join(choices(ascii_letters, k=10)),
            created_by=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductListViewTest(TestCase):
    fixtures = [
        "users-fixtures.json",
        "products-fixtures.json"
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:product_list"))
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=[p.name for p in response.context["products"]],
            transform=lambda product: product.name,
        )
        self.assertTemplateUsed(response, "shopapp/product_list.html")


class ProductsExportViewTest(TestCase):
    fixtures = [
        "users-fixtures.json",
        "products-fixtures.json",
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products-export"))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = {
            "products": [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": str(product.price),
                    "archived": product.archived,
                }
                for product in products
            ]
        }
        products_data = response.json()
        self.assertEqual(products_data, expected_data)


class OrderDetailViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username="testuser", password="testpass")
        cls.user = User.objects.create_user(**cls.credentials)
        cls.user.user_permissions.add(
            Permission.objects.get(codename="add_order")
        )
        cls.user.user_permissions.add(
            Permission.objects.get(codename="view_order")
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)
        self.order = Order.objects.create(
            user=self.user,
            delivery_address="Test address",
            promocode="TEST123",
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(reverse("shopapp:order_details", kwargs={"pk": self.order.pk}))
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context["object"].pk, self.order.pk)

class OrderExportViewTest(TestCase):
    fixtures = [
        "users-fixtures.json",
        "products-fixtures.json",
        "order-fixtures.json",
    ]
    def test_export_orders(self):
        response = self.client.get(reverse("shopapp:orders-export"))
        self.assertEqual(response.status_code, 200)

        orders = Order.objects.order_by("pk").all()
        expected_data = {
            "orders": [
                {
                    "pk": order.pk,
                    "delivery_address": order.delivery_address,
                    "promocode": order.promocode,
                    "user": order.user_id,
                    "products": [p.pk for p in order.products.all()],
                }
                for order in orders
            ]
        }
        orders_data = response.json()
        self.assertEqual(orders_data, expected_data)