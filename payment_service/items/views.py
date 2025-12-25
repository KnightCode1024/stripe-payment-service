from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView
from django.views.generic.list import ListView

from .models import Item, Order, Discount, Tax


class ItemView(DetailView):
    model = Item
    template_name = "item.html"
    context_object_name = "item"

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Item, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_publishable_key"] = settings.STRIPE_PUBLISHABLE_KEY
        return context

class ItemListView(ListView):
    model = Item
    template_name = "items.html"
    context_object_name = "items"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_publishable_key"] = settings.STRIPE_PUBLISHABLE_KEY
        return context


class CreateOrderView(TemplateView):
    template_name = "create_order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = Item.objects.all()
        context["discounts"] = Discount.objects.filter(is_active=True)
        context["taxes"] = Tax.objects.filter(is_active=True)
        context["stripe_publishable_key"] = settings.STRIPE_PUBLISHABLE_KEY
        return context
