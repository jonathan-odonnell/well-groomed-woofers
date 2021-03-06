from django.db import models
from profiles.models import UserProfile


class Contact(models.Model):

    class Meta:
        ordering = ('-date',)

    full_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='contact')
    date = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=50)
    message = models.TextField()

    def __str__(self):
        return f'{self.full_name} - {self.subject}'
