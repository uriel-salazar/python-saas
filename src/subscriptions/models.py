from django.db import models
from django.contrib.auth.models import Group,Permission
from django.conf import settings 


SUBCRIPTION_PERMISSIONS =  [
            ("advanced","Advanced Perm"),
            ("pro","Pro Perm"),
            ("basic","Basic Perm"),
            ("basic_ai","Basic AI Perm"),

        ]
class Subscription(models.Model):
    name =  models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    
    permissions = models.ManyToManyField(Permission,
    limit_choices_to = {
        "content_type__app_label":"subscriptions",
        "codename__in":[x[0] for x in SUBCRIPTION_PERMISSIONS
        ]
        }
    )
    class Meta:
        # subscriptions permissions 
        permissions = SUBCRIPTION_PERMISSIONS
