from django.contrib import admin
from .models import Item, OrderItem, Order, Discount, Tax
from .forms import ItemForm


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    form = ItemForm
    list_display = ["name", "get_price_display", "description"]

    def get_price_display(self, obj):
        return obj.price_display

    get_price_display.short_description = "Цена"
    get_price_display.admin_order_field = "price"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at", "is_paid", "get_total_amount_display", "discount", "tax"]
    list_filter = ["is_paid", "created_at", "discount", "tax"]
    readonly_fields = ["created_at", "stripe_session_id", "subtotal_amount_display", "discount_amount_display", "tax_amount_display", "total_amount_display"]

    def get_total_amount_display(self, obj):
        return obj.total_amount_display

    get_total_amount_display.short_description = "Общая сумма"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "item", "quantity", "get_total_price_display"]
    list_filter = ["order", "item"]

    def get_total_price_display(self, obj):
        return obj.total_price_display

    get_total_price_display.short_description = "Общая цена"


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ["name", "discount_type", "value", "is_active"]
    list_filter = ["discount_type", "is_active"]
    search_fields = ["name", "description"]


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ["name", "tax_type", "value", "is_active"]
    list_filter = ["tax_type", "is_active"]
    search_fields = ["name", "description"]
