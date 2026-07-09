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

def create_product(name = '',email = '',metadata = {},raw=False):
    response = stripe.Product.create(name = name,
                                      metadata=metadata)
    if raw:
        return response
    stripe_id=response.id
    return stripe_id

def create_price(currency = "usd",
                unit_amount = 9999,
                interval = "month",
                product = None,
                metadata = {},
                raw = False,
                ):
        if product is None:
            return None
        response =  stripe.Price.create(
            currency = currency,
            unit_amount = unit_amount,
            recurring = {"interval": interval},
            product = product,
            metadata = metadata 
        )
        if raw:
            return response
        stripe_id=response.id
        return stripe_id