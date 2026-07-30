from django.shortcuts import render
from subscriptions.models import SubscriptionPrice

def subscriptions_price_view(request,interval = "month"):
    qs  = SubscriptionPrice.objects.filter(featured = True)
    monthly_qs = SubscriptionPrice.objects.filter(
        interval = SubscriptionPrice.IntervalChoices.MONTHLY,
    )
    yearly_qs = SubscriptionPrice.objects.filter(
        interval = SubscriptionPrice.IntervalChoices.YEARLY,
    )
    object_list = interval = SubscriptionPrice.IntervalChoices.MONTHLY
    
    return render(request,"subscriptions/pricing.html",{
        "monthly_qs": monthly_qs,
        "yearly_qs": yearly_qs
    })