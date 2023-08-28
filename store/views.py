from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from store.pagination import DefaultPagination
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer
from .models import Product, Collection, OrderItem, Review
from .filters import ProductFilter


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer

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

    # overriding the queryset
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])
