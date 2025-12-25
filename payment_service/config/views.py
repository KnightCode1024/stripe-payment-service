from django.views.generic import RedirectView
from django.urls import reverse_lazy

class RedirectToItemsView(RedirectView):
    url = reverse_lazy("items_list")