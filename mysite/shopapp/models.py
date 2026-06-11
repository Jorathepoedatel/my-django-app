from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation.trans_null import gettext_lazy


def product_preview_directory_path(instance: "Product", filename) -> str:
    return f"products/product_{instance.pk}/preview/{filename}"


def product_image_directory_path(instance: "ProductImages", filename) -> str:
    return f"products/product_{instance.product.pk}/images/{filename}"

class Product(models.Model):
    class Meta:
        ordering = ["name", "price"]
        verbose_name = gettext_lazy("Product")
        verbose_name_plural = gettext_lazy("Products")

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True,db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2,db_index=True)
    discount = models.SmallIntegerField(default=0,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    preview_image = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})

class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(blank=True, null=True, upload_to=product_image_directory_path)
    description = models.CharField(max_length=250, null=False, blank=True)

class Order(models.Model):
    class Meta:
        verbose_name = gettext_lazy("Order")
        verbose_name_plural = gettext_lazy("Orders")
    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(null=True, blank=True, upload_to="orders/receipts/")
