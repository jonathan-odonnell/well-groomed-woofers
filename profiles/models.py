from django.db import models
from django.contrib.auth.models import User, Permission
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    billing information and order history
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(max_length=20)
    address_line_1 = models.CharField(max_length=80)
    address_line_2 = models.CharField(max_length=80, null=True, blank=True)
    town_or_city = models.CharField(max_length=40)
    county = models.CharField(max_length=80)
    postcode = models.CharField(max_length=20)
    country = CountryField(blank_label='Country *')

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile and adds permissions
    if user has been created
    """
    if created:
        if instance.is_superuser:
            permissions = Permission.objects.all()
            instance.user_permissions.set(permissions)
        UserProfile.objects.create(user=instance)
        instance.userprofile.save()
