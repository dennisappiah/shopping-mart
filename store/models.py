from uuid import uuid4
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    # products

    def __str__(self) -> str:
        return self.description


class Collection(models.Model):
    title = models.CharField(max_length=255)
    # products

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1, message="unit price cannot less than 1")],
    )
    inventory = models.IntegerField()
    last_update = models.DateTimeField(
        auto_now=True
    )  # date updates as Product object is updated
    collection = models.ForeignKey(
        Collection, related_name="products", on_delete=models.PROTECT
    )
    promotions = models.ManyToManyField(Promotion, related_name="products", blank=True)
    # orderitems
    # cartitems

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)


class Customer(models.Model):
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_SILVER, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    membership_status = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # orders
    # address

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        ordering = ["user__first_name", "user__last_name"]


class Order(models.Model):
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETED = "C"
    PAYMENT_STATUS_FAILED = "F"

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETED, "Completed"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    ]

    placed_at = models.DateTimeField(
        auto_now_add=True
    )  # date is auto-populated with the current date for the first time Order object is created
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="orders"
    )
    # orderitems


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="orderitems", on_delete=models.PROTECT
    )
    product = models.ForeignKey(
        Product, related_name="orderitems", on_delete=models.PROTECT
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, primary_key=True, related_name="address"
    )


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # cartitems


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartitems")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cartitems"
    )
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
