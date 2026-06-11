from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .views import ShopIndex, GroupsListView, \
    ProductsDetailsView, ProductsListView, OrdersListView, OrdersDetailsView, ProductCreateView, ProductUpdateView, \
    ProductDeleteView, OrdersCreateView, OrderUpdateView, OrderDeleteView, ProductsDataExportView, OrdersExportView, \
    ProductViewSet, OrderViewSet, LatestProductsFeed, UserOrdersListView, UserOrdersListExportView

app_name = "shopapp"


router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    path("", ShopIndex.as_view(), name="index"),
    path('api/', include(router.urls), name="api"),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="product_list"),
    path('products/create/', ProductCreateView.as_view(), name="product_create"),
    path('products/export', ProductsDataExportView.as_view(), name="products-export"),
    path("products/latest/feed/", LatestProductsFeed(), name="products-feed"),
    path("products/<int:pk>/",ProductsDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update",ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete",ProductDeleteView.as_view(), name="product_delete"),
    path("orders/", OrdersListView.as_view(), name="order_list"),
    path("orders/create", OrdersCreateView.as_view(), name="order_create"),
    path('orders/export', OrdersExportView.as_view(), name="orders-export"),
    path("orders/<int:pk>/",OrdersDetailsView.as_view(), name="order_details"),
    path("orders/<int:pk>/update",OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete",OrderDeleteView.as_view(), name="order_delete"),
    path('users/<int:user_id>/orders/', UserOrdersListView.as_view(), name='user_orders'),
    path('users/<int:user_id>/orders/export/', UserOrdersListExportView.as_view(), name='user_orders_export'),

]
