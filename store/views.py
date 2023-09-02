from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from store.pagination import DefaultPagination
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    ProductSerializer,
    CollectionSerializer,
    ReviewSerializer,
    UpdateCartItemSerializer,
    CustomerSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    UpdateOrderSerializer,
)
from .models import (
    Cart,
    CartItem,
    Product,
    Collection,
    OrderItem,
    Review,
    Customer,
    Order,
)
from .filters import ProductFilter
from .permissions import IsAdminOrViewOnly


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrViewOnly]

    def destroy(self, request, *args, **kwargs):
        collection_id = kwargs.get("pk")
        if Product.objects.filter(collection_id=collection_id).count() > 0:
            return Response(
                {
                    "error": "Collection cannot be deleted because it associated with product"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related("collection").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["title", "description"]
    ordering_fields = ["unit_price", "last_update"]
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrViewOnly]

    def destroy(self, request, *args, **kwargs):
        product_id = kwargs.get("pk")
        if OrderItem.objects.filter(product_id=product_id).count() > 0:
            return Response(
                {
                    "error": "Product cannot be deleted because it associated with an order item"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}

    # overriding the queryset to filter the product_pk from the request url
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    # overriding the serializer class to perform serialization based on the request method
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    # overriding the queryset to filter by cart_id
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related(
            "product"
        )

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}


# Customer Profile ViewSet
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    """
    - Admin should be able to see all orders, and detail operations
    - a customer should only be able to see his own order and not that of others
    """

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        elif self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        customer = Customer.objects.get(user_id=user.id)

        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer_id=customer.id)

    """Returning the created order object structure instead of cart_id from the CreateOrder serializer"""

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
