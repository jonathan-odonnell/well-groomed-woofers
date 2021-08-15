from django.db import models
from profiles.models import UserProfile


class Breed(models.Model):
    CHOICES = [
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
        ('Extra Large', 'Extra Large'),
    ]

    name = models.CharField(max_length=20)
    dog_size = models.CharField(max_length=20, choices=CHOICES)

    def __str__(self):
        return self.name


class Pet(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    breed = models.ForeignKey(
        Breed, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
