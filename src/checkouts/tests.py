
from django.urls import resolve, reverse

from checkouts import views


class CheckoutUrlTests(TestCase):
    def test_final_checkout_route_resolves_to_checkout_finalize_view(self):
        path = reverse('stripe-checkout-finalize')
        self.assertEqual(path, '/checkout/success/')
        self.assertEqual(resolve(path).func, views.checkout_finalize_view)
