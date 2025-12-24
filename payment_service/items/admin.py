from django.contrib import admin
from .models import Item
from .forms import ItemForm


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    form = ItemForm 
    list_display = ['name', 'get_price_display', 'description'] 
    
    def get_price_display(self, obj):
        return obj.price_display
    get_price_display.short_description = "Цена"
    get_price_display.admin_order_field = 'price' 