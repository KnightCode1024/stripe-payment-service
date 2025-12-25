from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator


class Item(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name="Название товара",
    )
    description = models.TextField(
        verbose_name="Описание товара",
    )
    price = models.IntegerField(  # Цена а копейках/центах
        verbose_name="Цена",
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    @property
    def price_decimal(self):
        return Decimal(self.price) / Decimal(100)

    @property
    def price_display(self):
        return f"{self.price_decimal:.2f} руб./$"


class Order(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии Stripe",
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name="Оплачен",
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def total_amount(self):
        total = 0
        for order_item in self.order_items.all():
            total += order_item.total_price
        return total

    @property
    def total_amount_display(self):
        return Decimal(self.total_amount) / Decimal(100)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Заказ",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name="Товар",
    )
    quantity = models.IntegerField(
        verbose_name="Количество",
        default=1,
        validators=[
            MinValueValidator(1),
        ],
        help_text="Количество единиц товара при заказе должно быть >= 1",
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"

    def __str__(self):
        return f"{self.item.name} x{self.quantity} (Заказ #{self.order.id})"

    @property
    def total_price(self):
        return self.item.price * self.quantity

    @property
    def total_price_display(self):
        return Decimal(self.total_price) / Decimal(100)


# class Discount(models.Model):
#     pass
#
#
# class Tax(models.Model):
#     pass
