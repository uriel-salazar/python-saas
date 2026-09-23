from decimal import Decimal
from typing import Any

import stripe

from django.core.management.base import BaseCommand

from subscriptions.models import Subscription, SubscriptionPrice
from helpers import billing


class Command(BaseCommand):
    def handle(self, *args, **options: Any):
        if not stripe.api_key:
            stripe.api_key = billing.STRIPE_SECRET_KEY

        products = {}
        for product in stripe.Product.list(limit=100).data:
            plan_id = product.metadata.to_dict().get("subscription_plan_id")
            key = plan_id if plan_id is not None else product.id
            products.setdefault(key, []).append(product)

        for key, product_list in products.items():
            product = self._pick_best_product(product_list)
            order = self._plan_order(key)
            sub, created = Subscription.objects.get_or_create(
                stripe_id=product.id,
                defaults={
                    "name": product.name,
                    "active": product.active,
                    "order": order,
                },
            )
            if not created:
                changed = False
                if sub.name != product.name:
                    sub.name = product.name
                    changed = True
                if sub.active != product.active:
                    sub.active = product.active
                    changed = True
                if order != sub.order:
                    sub.order = order
                    changed = True
                if changed:
                    sub.save()

            self._sync_prices(sub, product)

        self.stdout.write(self.style.SUCCESS("Stripe products and prices synced"))

    def _pick_best_product(self, product_list):
        best = None
        for product in product_list:
            price_count = len(
                stripe.Price.list(product=product.id, limit=100, active=True).data
            )
            if best is None or price_count > best[0]:
                best = (price_count, product)
        return best[1]

    def _plan_order(self, key):
        try:
            return int(key)
        except (TypeError, ValueError):
            return -1

    def _sync_prices(self, sub, product):
        seen = set()
        prices = stripe.Price.list(product=product.id, limit=100, active=True).data
        prices.sort(key=lambda p: p.created, reverse=True)
        for price in prices:
            recurring = getattr(price, "recurring", None)
            recurring = recurring.to_dict() if recurring else {}
            interval = recurring.get("interval")
            if interval not in (
                SubscriptionPrice.IntervalChoices.MONTHLY,
                SubscriptionPrice.IntervalChoices.YEARLY,
            ):
                continue
            key = (price.currency, interval)
            if key in seen:
                continue
            seen.add(key)
            amount = Decimal(price.unit_amount) / Decimal(100)
            SubscriptionPrice.objects.get_or_create(
                stripe_id=price.id,
                defaults={
                    "subscription": sub,
                    "interval": interval,
                    "price": amount,
                    "featured": True,
                },
            )