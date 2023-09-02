from typing import Any
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from store.models import Product, Customer, Order, Collection, OrderItem


# Register your models here.
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]
    search_fields = ["title"]

    @admin.display(ordering="products_count")
    def products_count(self, collection: Collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": collection.id})
        )
        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    # overriding the base queryset to annotate `products_count`
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count("products"))


# customising list_filter attribute of ProductAdmin
class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [("<10", "Low")]

    def queryset(self, request, queryset):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "unit_price",
        "inventory",
        "inventory_status",
        "collection_title",
    ]
    list_editable = ["unit_price"]
    list_per_page = 10
    list_select_related = ["collection"]
    list_filter = ["collection", "last_update", InventoryFilter]
    search_fields = ["title"]
    actions = ["clear_inventory"]
    # customising the Product Add form
    autocomplete_fields = ["collection"]
    prepopulated_fields = {"slug": ["title"]}

    # Adding computed columns -> custom row level computation
    @admin.display(ordering="inventory")
    def inventory_status(self, product: Product):
        if product.inventory < 10:
            return "Low"
        return "OK"

    # selecting related field
    def collection_title(self, product: Product) -> str:
        return product.collection.title

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request, f"{updated_count} products were successfully updated.", messages
        )

    class Media:
        css = {"all": ["store/styles.css"]}


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership_status"]
    list_editable = ["membership_status"]
    list_select_related = ["user"]
    ordering = ["user__first_name", "user__last_name"]
    list_per_page = 10
    search_fields = ["first_name__istartswith", "last_name__istartswith"]
    autocomplete_fields = ["user"]


# managing children models using inlines(orderItems)
class OrderItemsInline(admin.TabularInline):
    model = OrderItem
    autocomplete_fields = ["product"]
    extra = 0
    min_num = 0
    max_num = 10


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer"]
    inlines = [OrderItemsInline]
