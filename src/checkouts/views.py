from django.shortcuts import redirect,render
from django.contrib.auth.decorators import login_required
from django.conf import settings 
from django.contrib.auth import get_user_model 
from subscriptions.models import SubscriptionPrice,Subscription,UserSubscription
import helpers.billing
from django.http import HttpResponseBadRequest
from django.urls import reverse
# Create your views here.

User = get_user_model()
BASE_URL = settings.BASE_URL 
def product_price_redirect_view(request,price_id = None, *args, **kwargs):
    request.session['checkout_subscription_price_id']  = price_id 
    return redirect('stripe-checkout-start')

@login_required
def checkout_redirect_view(request):
    
    checkout_subscription_price_id =  request.session.get(
        "checkout_subscription_price_id")
    try :
        obj  = SubscriptionPrice.objects.get(
        id = checkout_subscription_price_id)
        
    except:
        obj = None 
    if checkout_subscription_price_id is None or obj is None :
        return redirect("pricing")
    customer_stripe_id = request.user.customer.stripe_id
    print(customer_stripe_id)
    
    success_url_path = reverse("stripe-checkout-finalize")
    pricing_url_path = reverse("pricing")
    success_url = f"{BASE_URL}{success_url_path}"
    cancel_url = f"{BASE_URL}{pricing_url_path}"
    price_stripe_id = obj.stripe_id 
    session_url = helpers.billing.start_session_checkout(
        customer_stripe_id,
        success_url = success_url,
        cancel_url = cancel_url,
        price_stripe_id = price_stripe_id,
        raw=False
    )
    return redirect(session_url)


def checkout_finalize_view(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponseBadRequest("Missing session_id")

    try:
        customer_id, plan_id = helpers.billing.checkout_customer_plan(
            session_id
        )
    except Exception:
        return HttpResponseBadRequest("Invalid checkout session")

    try:
        price_obj = SubscriptionPrice.objects.get(stripe_id=plan_id)
        sub_obj = price_obj.subscription
    except SubscriptionPrice.DoesNotExist:
        sub_obj = None

    try:
        user_obj = User.objects.get(customer__stripe_id=customer_id)
    except User.DoesNotExist:
        user_obj = None

    if sub_obj is None or user_obj is None:
        return HttpResponseBadRequest("there was an error...")

    _user_sub_obj, created = UserSubscription.objects.update_or_create(
        user=user_obj,
        defaults={"subscription": sub_obj, "active": True}
    )

    context = {}
    return render(request, "checkout/success.html", context)

 