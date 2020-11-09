from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from .models import CustomerProfile

def customer_profile(sender, instance, created, **kwargs):
    if created:
        # For every user registration, add user to customer group
        # group = Group.objects.get(name='customer')
        # instance.groups.add(group)

        CustomerProfile.objects.create(
            user=instance, 
            first_name=instance.first_name, 
            last_name=instance.last_name, 
            email=instance.email,
            phone='-'
            )

        print("Customer Profile Created!")

post_save.connect(customer_profile, sender=User)