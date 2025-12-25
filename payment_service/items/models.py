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


class OrderItem(models.Model):
    quantity = models.IntegerField(
        verbose_name="Количество",
        default=1,
        validators=[
            MinValueValidator(1),
        ],
        help_text="Количество единиц товара при заказе должно быть >= 1",
    )
    item = models.OneToOneField(
        Item,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class Order(models.Model):
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="order_items",
    )


# class Discount(models.Model):
#     pass
#
#
# class Tax(models.Model):
#     pass
