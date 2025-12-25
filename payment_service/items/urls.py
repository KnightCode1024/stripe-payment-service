from django.urls import path

from . import views

urlpatterns = [
    path(
        "<int:pk>/",
        views.ItemView.as_view(),
        name="item_detail",
    ),
    path(
        "",
        views.ItemListView.as_view(),
        name="items_list",
    )
]
