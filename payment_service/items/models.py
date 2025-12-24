from decimal import Decimal

from django.db import models


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
    pass


class Discount(models.Model):
    pass

class Tax(models.Model):
    pass