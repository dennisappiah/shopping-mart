from rest_framework import serializers
from .models import (
    Product,
    Collection,
    Review,
    Cart,
    CartItem,
    Customer,
    Order,
    OrderItem,
)
from decimal import Decimal
from django.db import transaction


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ["id", "title", "products_count"]


class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "unit_price",
            "inventory",
            "collection",
            "price_with_tax",
        ]

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "date", "name", "description"]

    def save(self, **kwargs):
        product_id = self.context["product_id"]
        Review.objects.create(product_id=product_id, **self.validated_data)


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]

    """
    - overriding the save method to encapsulates the logic for creating a cart item before save
    
    - With the save method, creating a new instance and/or updating an existing instance
    """

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        try:
            # update an existing instance
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity = cart_item.quantity + quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # create a new instance
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )
        return self.instance

    def validate_product_id(self, product_id):
        if not Product.objects.filter(pk=product_id).exists():
            raise serializers.ValidationError("No product with the given id was found")
        return product_id


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CustomProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = CustomProductSerializer()
    total_price = serializers.SerializerMethodField(method_name="calculate_total_price")

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]

    def calculate_total_price(self, cartItem: CartItem):
        return cartItem.product.unit_price * cartItem.quantity


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]

    def get_total_price(self, cart: Cart):
        total_price = sum(
            [item.quantity * item.product.unit_price for item in cart.items.all()]
        )
        return total_price


# Customer Profile Serializer
class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership_status"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = CustomProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "placed_at", "payment_status", "customer", "items"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    """
    - A customer/user should be the only one to create his own order
    
    - overriding the save method to encapsulates the logic for creating an order before save
    """

    def save(self, **kwargs):
        with transaction.atomic():
            user_id = self.context["user_id"]
            cart_id = self.validated_data["cart_id"]
            customer = Customer.objects.get(user_id=user_id)

            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.select_related("product").filter(
                cart_id=cart_id
            )

            # transforming cart_items to order-item objects to create order-items
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.unit_price,
                )
                for item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)

            # after order, delete cart
            Cart.objects.filter(pk=cart_id).delete()

            return order

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No cart with the given id was found")
        return cart_id


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["payment_status"]
