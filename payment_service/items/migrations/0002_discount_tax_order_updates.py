# Generated manually with proper migration logic

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def create_default_order_for_orphaned_orderitems(apps, schema_editor):
    """Создает фиктивный заказ для OrderItem записей без заказа"""
    Order = apps.get_model('items', 'Order')
    OrderItem = apps.get_model('items', 'OrderItem')

    # Находим OrderItem без заказа
    orphaned_orderitems = OrderItem.objects.filter(order__isnull=True)

    if orphaned_orderitems.exists():
        # Создаем фиктивный заказ
        default_order = Order.objects.create(
            stripe_session_id=None,
            is_paid=False
        )

        # Привязываем все orphaned OrderItem к этому заказу
        orphaned_orderitems.update(order=default_order)


def reverse_create_default_order_for_orphaned_orderitems(apps, schema_editor):
    """Обратная операция - отвязываем OrderItem от фиктивного заказа"""
    Order = apps.get_model('items', 'Order')
    OrderItem = apps.get_model('items', 'OrderItem')

    # Находим заказы без stripe_session_id (фиктивные)
    default_orders = Order.objects.filter(stripe_session_id__isnull=True, is_paid=False)

    for order in default_orders:
        # Отвязываем OrderItem от фиктивного заказа
        OrderItem.objects.filter(order=order).update(order=None)
        # Удаляем фиктивный заказ
        order.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Discount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Название скидки"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Описание скидки"),
                ),
                (
                    "discount_type",
                    models.CharField(
                        choices=[
                            ("percent", "Процент"),
                            ("fixed", "Фиксированная сумма"),
                        ],
                        default="percent",
                        max_length=10,
                        verbose_name="Тип скидки",
                    ),
                ),
                (
                    "value",
                    models.DecimalField(
                        decimal_places=2,
                        help_text=(
                            "Для процента: 0-100, для фиксированной",
                            "суммы: значение в копейках/центах",
                        ),
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Значение скидки",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активна"),
                ),
            ],
            options={
                "verbose_name": "Скидка",
                "verbose_name_plural": "Скидки",
            },
        ),
        migrations.CreateModel(
            name="Tax",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Название налога"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Описание налога"),
                ),
                (
                    "tax_type",
                    models.CharField(
                        choices=[
                            ("percent", "Процент"),
                            ("fixed", "Фиксированная сумма"),
                        ],
                        default="percent",
                        max_length=10,
                        verbose_name="Тип налога",
                    ),
                ),
                (
                    "value",
                    models.DecimalField(
                        decimal_places=2,
                        help_text=(
                            "Для процента: 0-100, для фиксированной суммы:",
                            "значение в копейках/центах",
                        ),
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Значение налога",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активен"),
                ),
            ],
            options={
                "verbose_name": "Налог",
                "verbose_name_plural": "Налоги",
            },
        ),
        migrations.AddField(
            model_name="order",
            name="discount",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="items.discount",
                verbose_name="Скидка",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="tax",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="items.tax",
                verbose_name="Налог",
            ),
        ),
        migrations.RunPython(
            create_default_order_for_orphaned_orderitems,
            reverse_create_default_order_for_orphaned_orderitems,
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_items",
                to="items.order",
                verbose_name="Заказ",
            ),
        ),
    ]
