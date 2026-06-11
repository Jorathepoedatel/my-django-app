from rest_framework import serializers
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'pk',
            'name',
            'price',
            'description',
            'discount',
            'created_at',
            'archived',
            'created_by',
            'preview_image',
        )

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'pk',
            'delivery_address',
            'promocode',
            'created_at',
            'user',
            'products',
            'receipt'
        )