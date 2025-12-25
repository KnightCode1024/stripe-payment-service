from django.conf import settings
from django.views.generic import DetailView, TemplateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.db import transaction
import stripe
import json

from items.models import Item, Order, OrderItem

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


class CreateOrderCheckoutSessionView(View):
    """Создание Stripe Checkout сессии для заказа с несколькими товарами"""

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            items_data = data.get('items', [])
            discount_id = data.get('discount_id')
            tax_id = data.get('tax_id')

            if not items_data:
                return JsonResponse({'error': 'Не указаны товары для заказа'}, status=400)

            # Создаем заказ в транзакции
            with transaction.atomic():
                order = Order.objects.create()

                # Добавляем товары в заказ
                for item_data in items_data:
                    item_id = item_data.get('item_id')
                    quantity = item_data.get('quantity', 1)

                    try:
                        item = Item.objects.get(id=item_id)
                        OrderItem.objects.create(
                            order=order,
                            item=item,
                            quantity=quantity
                        )
                    except Item.DoesNotExist:
                        return JsonResponse({'error': f'Товар с ID {item_id} не найден'}, status=400)

                # Применяем скидку и налог, если указаны
                if discount_id:
                    try:
                        from items.models import Discount
                        discount = Discount.objects.get(id=discount_id, is_active=True)
                        order.discount = discount
                        order.save()
                    except Discount.DoesNotExist:
                        pass  # Игнорируем несуществующие скидки

                if tax_id:
                    try:
                        from items.models import Tax
                        tax = Tax.objects.get(id=tax_id, is_active=True)
                        order.tax = tax
                        order.save()
                    except Tax.DoesNotExist:
                        pass  # Игнорируем несуществующие налоги

            # Создаем line_items для Stripe
            line_items = []

            # Добавляем товары
            for order_item in order.order_items.all():
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': order_item.item.name,
                            'description': order_item.item.description or None,
                        },
                        'unit_amount': order_item.item.price
                    },
                    'quantity': order_item.quantity,
                })

            # Добавляем скидку, если есть
            discounts = []
            if order.discount:
                if order.discount.discount_type == 'percent':
                    discounts.append({
                        'coupon': self._create_or_get_stripe_coupon(order.discount)
                    })
                # Для фиксированной скидки нужно использовать другой подход
                # (например, через отрицательные line_items)

            # Добавляем налог, если есть
            tax_rates = []
            if order.tax:
                if order.tax.tax_type == 'percent':
                    tax_rates.append(self._create_or_get_stripe_tax_rate(order.tax))

            # Создаем сессию Stripe Checkout
            session_data = {
                'line_items': line_items,
                'mode': 'payment',
                'success_url': request.build_absolute_uri(reverse('success')),
                'cancel_url': request.build_absolute_uri(reverse('cancel')),
                'metadata': {
                    'order_id': str(order.id)
                }
            }

            if discounts:
                session_data['discounts'] = discounts

            if tax_rates:
                session_data['automatic_tax'] = {'enabled': False}  # Отключаем автоматический налог
                session_data['line_items'][-1]['tax_rates'] = tax_rates  # Применяем налог к последнему товару

            session = stripe.checkout.Session.create(**session_data)

            # Сохраняем ID сессии в заказе
            order.stripe_session_id = session.id
            order.save()

            return JsonResponse({'id': session.id, 'order_id': order.id})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный JSON'}, status=400)
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)

    def _create_or_get_stripe_coupon(self, discount):
        """Создает или получает существующий купон в Stripe для скидки"""
        # В реальном проекте здесь должна быть логика кеширования/проверки существования купона
        coupon_data = {
            'name': discount.name,
            'percent_off': float(discount.value) if discount.discount_type == 'percent' else None,
            'amount_off': int(discount.value * 100) if discount.discount_type == 'fixed' else None,  # В центах
            'currency': 'usd' if discount.discount_type == 'fixed' else None,
        }

        # Убираем None значения
        coupon_data = {k: v for k, v in coupon_data.items() if v is not None}

        coupon = stripe.Coupon.create(**coupon_data)
        return coupon.id

    def _create_or_get_stripe_tax_rate(self, tax):
        """Создает или получает существующий tax rate в Stripe для налога"""
        # В реальном проекте здесь должна быть логика кеширования/проверки существования tax rate
        tax_rate_data = {
            'display_name': tax.name,
            'percentage': float(tax.value) if tax.tax_type == 'percent' else None,
            'inclusive': False,  # Налог добавляется к цене
        }

        # Убираем None значения
        tax_rate_data = {k: v for k, v in tax_rate_data.items() if v is not None}

        tax_rate = stripe.TaxRate.create(**tax_rate_data)
        return tax_rate.id