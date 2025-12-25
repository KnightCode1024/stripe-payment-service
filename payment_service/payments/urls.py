from django.urls import path

from . import views

urlpatterns = [
    path(
        "success/",
        views.SuccessView.as_view(),
        name="success",
    ),
    path(
        "cancel/",
        views.CancelView.as_view(),
        name="cancel",
    ),
    path(
        "<int:pk>/",
        views.CreateCheckoutStripeSessionView.as_view(),
        name="create_checkout_session",
    ),
]
