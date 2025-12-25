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
    discount = models.ForeignKey(
        "Discount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Скидка",
    )
    tax = models.ForeignKey(
        "Tax",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Налог",
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def subtotal_amount(self):
        total = 0
        for order_item in self.order_items.all():
            total += order_item.total_price
        return total

    @property
    def discount_amount(self):
        if not self.discount or not self.discount.is_active:
            return 0

        if self.discount.discount_type == "percent":
            return int(self.subtotal_amount * (self.discount.value / 100))
        else:
            return min(int(self.discount.value), self.subtotal_amount)

    @property
    def tax_amount(self):
        """Расчет суммы налога"""
        if not self.tax or not self.tax.is_active:
            return 0

        amount_after_discount = self.subtotal_amount - self.discount_amount

        if self.tax.tax_type == "percent":
            return int(amount_after_discount * (self.tax.value / 100))
        else:
            return int(self.tax.value)

    @property
    def total_amount(self):
        return self.subtotal_amount - self.discount_amount + self.tax_amount

    @property
    def total_amount_display(self):
        return Decimal(self.total_amount) / Decimal(100)

    @property
    def subtotal_amount_display(self):
        return Decimal(self.subtotal_amount) / Decimal(100)

    @property
    def discount_amount_display(self):
        return Decimal(self.discount_amount) / Decimal(100)

    @property
    def tax_amount_display(self):
        return Decimal(self.tax_amount) / Decimal(100)


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


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percent", "Процент"),
        ("fixed", "Фиксированная сумма"),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Название скидки",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание скидки",
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default="percent",
        verbose_name="Тип скидки",
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Значение скидки",
        help_text=(
            "Для процента: 0-100, для фиксированной",
            "суммы: значение в копейках/центах",
        ),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"

    def __str__(self):
        if self.discount_type == "percent":
            return f"{self.name} ({self.value}%)"
        else:
            return f"{self.name} ({Decimal(self.value) / Decimal(100):.2f} руб./$)"


class Tax(models.Model):
    TAX_TYPE_CHOICES = [
        ("percent", "Процент"),
        ("fixed", "Фиксированная сумма"),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Название налога",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание налога",
    )
    tax_type = models.CharField(
        max_length=10,
        choices=TAX_TYPE_CHOICES,
        default="percent",
        verbose_name="Тип налога",
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Значение налога",
        help_text=(
            "Для процента: 0-100, для фиксированной суммы:",
            "значение в копейках/центах",
        ),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )

    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"

    def __str__(self):
        if self.tax_type == "percent":
            return f"{self.name} ({self.value}%)"
        else:
            return (
                f"{self.name}",
                f" ({Decimal(self.value) / Decimal(100):.2f} руб./$)",
            )
