import stripe
from decouple import config
from django.core.exceptions import ImproperlyConfigured

DJANGO_DEBUG = config("DEBUG", default=False, cast=bool)
STRIPE_SECRET_KEY = config(
    "STRIPE_SECRET_KEY",
    default=config(
        "STRIPE_API_KEY",
        default=config("STRIPE.API_KEY", default="", cast=str),
        cast=str,
    ),
    cast=str,
)

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
else:
    stripe.api_key = None

if "sk_test" in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError("Invalid Stripe key for prod")


def create_customer(name = '',email = '',metadata = {},raw=False):

    response = stripe.Customer.create(name = name, email=email,
                                      metadata=metadata)
    if raw:
        return response
    stripe_id=response.id
    return stripe_id

