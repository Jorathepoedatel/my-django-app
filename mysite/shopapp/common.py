import csv
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding):
    csvfile = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = csv.DictReader(csvfile)
    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csvfile = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = csv.DictReader(csvfile)
    orders = []

    for row in reader:
        order = Order.objects.create(
            delivery_address=row["delivery_address"],
            promocode=row.get("promocode", ""),
            created_by_id=row["created_by"],
        )

        product_ids = [pid.strip() for pid in row.get("products", "").split(";") if pid.strip()]

        if not product_ids:
            order.delete()
            raise ValueError(f"Заказ '{order.delivery_address}' не содержит ни одного продукта")

        for pid in product_ids:
            try:
                product = Product.objects.get(pk=pid)
                order.products.add(product)
            except Product.DoesNotExist:
                order.delete()
                raise ValueError(f"Продукт с ID={pid} не найден")

        orders.append(order)

    return orders
