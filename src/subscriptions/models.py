from django.db import models

class SubscriptionModels(models.Model):
    name=models.CharField(max_length=100)

    class Meta:
        # subscriptions permissions 
        permissions=[
            ("advanced","Advanced Perm"),
            ("pro","Pro Perm"),
            ("basic","Basic Perm"),
            ("basic_ai","Basic AI Perm"),

        ]