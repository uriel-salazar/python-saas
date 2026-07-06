import stripe
from decouple import config
DJANGO_DEBUG = config("DEBUG",default = False, cast= bool) 
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY",default="",cast= str)

if "sk_test" in STRIPE_SECRET_KEY and not  DJANGO_DEBUG:
    raise ValueError("Invalid Stripe key for prod")

def create_costumer():
    stripe.Customer.create(
    name = "Jenny Rosen",
    email = "jennyrosen@example.com",
    )

