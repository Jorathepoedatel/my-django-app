import logging
from csv import DictWriter
from dataclasses import fields
from timeit import default_timer

from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .common import save_csv_products
from .forms import GroupsForm, ProductForm
from .models import Product, Order, ProductImages
from .serializers import ProductSerializer, OrderSerializer

logger = logging.getLogger(__name__)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        'name',
        'description',
    ]
    ordering_fields = [
        'pk',
        'name',
        'description',
        'price',
    ]
    filterset_fields = (
        'name',
        'description',
        'price',
        'discount',
        'archived',
    )

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print('YOYO')
        return super().list(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = "product-export.csv"
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(
        detail=False,
        methods=['post'],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request) -> Response:
        products = save_csv_products(
            request.FILES['file'].file,
            request.encoding
        )
        serializer = self.get_serializer(data=products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        'delivery_address',
        'promocode',
    ]
    ordering_fields = [
        'pk',
        'user',
        'created_at',
    ]
    filterset_fields = (
        'delivery_address',
        'promocode',
        'user',
        'products',
    )


class ShopIndex(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        logger.debug("Products for shop index: %s", products)
        logger.info("Rendering shop index page")
        print('shop index context', context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupsForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupsForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(reverse('shopapp:groups_list'))


class ProductsDetailsView(DetailView):
    template_name = "shopapp/product_details.html"
    # model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/product_list.html"
    model = Product
    queryset = Product.objects.filter(archived=False)
    context_object_name = "products"


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    model = Product
    # fields = ["name", "price", "description", "discount","preview_image"]
    success_url = reverse_lazy('shopapp:product_list')
    form_class = ProductForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImages.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        product = self.get_object()
        user = self.request.user
        if user.is_superuser:
            return True
        return user.has_perm('shopapp.add_product') and product.created_by == user

    model = Product
    # fields = ["name", "price", "description", "discount", "preview_image"]
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImages.objects.create(
                product=self.object,
                image=image,
            )
        return response

    def get_success_url(self):
        return reverse('shopapp:product_details', kwargs={'pk': self.object.pk})


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:product_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class LatestProductsFeed(Feed):
    title = "Shop products"
    link = "/shopapp/"
    description = "Latest products in shop"

    def items(self):
        return Product.objects.filter(archived=False).order_by("-created_at")[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description_short


class OrdersListView(ListView):
    template_name = "shopapp/order_list.html"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products"))


class OrdersDetailsView(LoginRequiredMixin, DetailView):
    template_name = "shopapp/order_details.html"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products"))


class OrdersCreateView(CreateView):
    model = Order
    fields = ['user', 'products', 'delivery_address', 'promocode']
    success_url = reverse_lazy('shopapp:order_list')


class OrderUpdateView(UpdateView):
    model = Order
    fields = ['user', 'products', 'delivery_address', 'promocode']
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse('shopapp:order_details', kwargs={'pk': self.object.pk})


class OrderDeleteView(DeleteView):
    template_name = "shopapp/order_delete.html"
    model = Order
    success_url = reverse_lazy('shopapp:order_list')


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if not products_data:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set("products_data_export", products_data, 300)
        return JsonResponse({cache_key: products_data})


class OrdersExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user_id,
                "products": [p.pk for p in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shopapp/user_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        self.owner = get_object_or_404(User, pk=self.kwargs['user_id'])
        return Order.objects.filter(user=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context

class UserOrdersListExportView(View):
    def get(self, request: HttpRequest,**kwargs) -> JsonResponse:
        cache_key = f"user_orders_export_{self.kwargs['user_id']}"
        orders_data = cache.get(cache_key)
        if not orders_data:
            owner = get_object_or_404(User, pk=self.kwargs['user_id'])
            orders = Order.objects.filter(user=owner).order_by('pk')
            serializer = OrderSerializer(orders, many=True)
            orders_data = serializer.data
            cache.set(cache_key, orders_data, 300)
        return JsonResponse({"orders": orders_data})