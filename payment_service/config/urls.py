from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("item/", include("items.urls")),
    path("buy/", include("payments.urls")),
    path("/", views.RedirectToItemsView.as_view())
]
