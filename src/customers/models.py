from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import helpers.billing
from allauth.account.signals import (
    user_signed_up as allauth_user_signed_up,
    email_confirmed as allauth_user_confirmed
)
# Create your models here.
User = settings.AUTH_USER_MODEL


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    stripe_id = models.CharField(max_length =  120, null = True, blank = True)
    init_email = models.EmailField(blank = True,null = False)
    init_email_confirmed=models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        
        if not self.stripe_id:
            if self.init_email_confirmed and self.init_email:  
                email = self.init_email
                if email and email != ' ': 
                    stripe_id = helpers.billing.create_customer(email=email,
                    metadata = {"user_id":self.user.id, "username":self.user.username},raw = False)
                    self.stripe_id = stripe_id
        super().save(*args, **kwargs)


@receiver(pre_delete, sender=get_user_model())
def delete_customer_for_user(sender, instance, **kwargs):
    if instance.pk is not None:
        Customer.objects.filter(user_id=instance.pk).delete()


def allauth_user_signed_up_handler(request,user,*args, **kwargs):
    email = user.email 
    Customer.objects.create(
        user = user,
        init_email = email,
        init_email_confirmed = False,
        
    )

allauth_user_signed_up.connect(allauth_user_signed_up_handler)


def allauth_user_email_handler(request,email_address,*args, **kwargs):
    qs = Customer.objects.filter(
        init_email = email_address,
        init_email_confirmed = False,
        
    )
    for obj in qs:
        obj.init_email_confirmed = True
        # send the signal 
        obj.save()

allauth_user_confirmed.connect(allauth_user_email_handler)