from django.db import models
from django.conf import settings 
import helpers.billing 
# Create your models here.
User = settings.AUTH_USER_MODEL


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        self.stripe_id = "somethig_niceee"
     #   stripe_response = helpers.billing.create_customer(raw = True)
     #   print(stripe_response)
        super().save(*args, **kwargs)