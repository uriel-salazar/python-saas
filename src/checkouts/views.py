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
    checkout_data = helpers.billing.get_checkout_customer_plan(session_id)
    data = {
            "customer_id":customer_id,
            'plan_id':sub_plan, 
            'sub_stripe_id':sub_stripe_id,
            'current_period_start':sub_r.current_period_start,
            'currrent_period_end':sub_r.current_period_end
    }
    plan_id = checkout_data.get('plan_id')
    customer_id = checkout_data.get('customer_id')
    sub_stripe_id = checkout_data.get('sub_stripe_id')
    current_period_start = checkout_data.get('current_period_start')
    current_period_end = checkout_data.get('current_period_end')

    if not session_id:
        return HttpResponseBadRequest("Missing session_id")

    try:
        customer_id, plan_id,sub_stripe_id = helpers.billing.get_checkout_customer_plan(
            session_id
        )
    except Exception:
        return HttpResponseBadRequest("Invalid checkout session")

    try:
        price_obj = SubscriptionPrice.objects.get(stripe_id=plan_id)
        sub_obj = price_obj.subscription
    except SubscriptionPrice.DoesNotExist:
        sub_stripe_id =sub_stripe_id 
        sub_obj = None

    updated_sub_options = {
        'subscription':sub_obj,
        'stripe_id':sub_stripe_id,
        'user_cancelled':False
    }
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
    
    if _user_sub_obj:
        # cancel old subscription
        old_stripe_id =  _user_sub_obj.stripe_id 
        same_stripe_id = _user_sub_obj == old_stripe_id
        if old_stripe_id is not same_stripe_id:
            try:
                helpers.billing.cancel_subscription(old_stripe_id,
                    reason='Auto ended membership')
            except:
                pass
            
            
        for k,v in updated_sub_options.items():
            setattr(_user_sub_obj,k,v)
            _user_sub_obj.save()
    context = {}
    return render(request, "checkout/success.html", context)

 