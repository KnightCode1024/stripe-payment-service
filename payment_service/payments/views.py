from django.conf import settings
from django.views.generic import DetailView, TemplateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
import stripe

from items.models import Item

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelView(TemplateView):
    template_name = 'cancel.html'


class CreateCheckoutStripeSessionView(DetailView):
    model = Item

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response()

    def render_to_response(self):
        item = self.object

        try:
            session = stripe.checkout.Session.create(
                line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': item.name,
                    'description': item.description or None,
                    },
                    'unit_amount': item.price
                },
                'quantity': 1,
                }],
                mode='payment',
                success_url=self.request.build_absolute_uri(reverse('success')),
                cancel_url=self.request.build_absolute_uri(reverse('cancel')),
            )
            return JsonResponse({'id': session.id})
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)