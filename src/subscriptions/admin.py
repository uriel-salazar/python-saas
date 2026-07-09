from django.contrib import admin

# Register your models here.
from .models import Subscription,UserSubscription,SubscriptionPrice

class SubscriptionPrice(admin.TabularInline):
    model = SubscriptionPrice
    extra = 2
    
class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionPrice]
    list_display = ['name','active']
    
admin.site.register(Subscription,SubscriptionAdmin)

admin.site.register(UserSubscription)
