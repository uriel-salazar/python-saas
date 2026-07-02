from django.db import models
from django.contrib.auth.models import Group,Permission
from django.conf import settings 
from django.db.models.signals import post_save
User= settings.AUTH_USER_MODEL

ALLOW_COSTUM_GROUPS = True
SUBCRIPTION_PERMISSIONS = [
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
    
    def __str__(self):
        return self.name 
    class Meta:
        # subscriptions permissions 
        permissions = SUBCRIPTION_PERMISSIONS
        
        
class UserSubscription(models.Model):
    # If the user is deleted the subscription will be deleted as well
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL,
    null = True,blank = True)
    active= models.BooleanField(default = True)
    
def user_post_save(sender,instance,*args,**kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user 
    subscription_obj = user_sub_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list("id",flat = True)
    
    if not ALLOW_COSTUM_GROUPS:   
         user.groups.set(groups_ids)
    else:
        subs_qs = Subscription.objects.filter(active = True).exclude(id = subscription_obj.id) if subscription_obj is not None else Subscription.objects.none()
        subs_groups = subs_qs.values_list("groups__id", flat = True)
        subs_groups_set = set(subs_groups)
        current_groups = user.groups.all().values_list("id",flat = True)
        groups_ids_sets = set(groups_ids) 
        current_groups_set = set(current_groups) - subs_groups_set
        final_group_lists = list(groups_ids_sets | current_groups_set)
        user.groups.set(final_group_lists) #concatenate them in a set 
        
    
post_save.connect(user_post_save,sender = UserSubscription)
    
