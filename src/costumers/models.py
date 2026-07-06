from django.db import models
from django.conf import settings 
# Create your models here.
User = settings.AUTH_USER_MODEL
class Costumer(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True,blank = True)
    
    
    def __str__(self):
        return "{self.user.name}"