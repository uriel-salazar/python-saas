import helpers.billing
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from subscriptions.models import SubscriptionPrice,UserSubscription
from django.urls import reverse

@login_required
def user_subscription_view(request):
    """ 
    Find an exsiting subscription for the user logged-in user 
    if one doesn't exist, it creates it
    
    Return : Status data subscription to the user
    """
    user_sub_obj, _ = UserSubscription.objects.get_or_create(
        user = request.user)
    sub_data = user_sub_obj.serialize()

    if user_sub_obj.stripe_id:
        try:
            stripe_sub = helpers.billing.get_subscription(
                user_sub_obj.stripe_id, raw=True)
            sub_data = helpers.billing.serialize_subscription_data(stripe_sub)

            user_sub_obj.status = sub_data["status"]
            user_sub_obj.current_period_start = sub_data["current_period_start"]
            user_sub_obj.current_period_end = sub_data["current_period_end"]
            user_sub_obj.active = sub_data["status"] in ("active", "trialing")
            user_sub_obj.user_cancelled = (
                sub_data["cancel_at_period_end"]
                or sub_data["status"] == "canceled"
            )
            user_sub_obj.save()
        except Exception:
            pass

    if request.method == 'POST':
        return redirect(user_sub_obj.get_absolute_url())

    return render (request, 'subscriptions/user_detail_view.html',
    {"subscription" : sub_data})
    
def subscriptions_price_view(request,interval = "month"):
    qs  = SubscriptionPrice.objects.filter(featured = True)
    inv_mo = SubscriptionPrice.IntervalChoices.MONTHLY
    inv_yr = SubscriptionPrice.IntervalChoices.YEARLY
    url_path_name = "pricing_interval"
    mo_url = reverse(url_path_name,kwargs = {"interval":inv_mo})
    yr_url = reverse(url_path_name,kwargs = {"interval":inv_yr})
    active = inv_mo
    
    object_list =   qs.filter(interval = inv_mo)
    
    if interval == inv_yr:
        active = inv_yr
        object_list = qs.filter(interval = inv_yr)
        
        
    return render(request,"subscriptions/pricing.html",{
        "object_list":object_list,
        "mo_url":mo_url,
        "yr_url":yr_url,
        "active":active
    })