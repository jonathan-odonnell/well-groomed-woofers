from django.db import models
from django.utils.timezone import localtime, now
from django.conf import settings
from datetime import timedelta
import redis


class Service(models.Model):
    class Meta:
        ordering = ('id',)

    name = models.CharField(max_length=254)
    image = models.ImageField()
    description = models.TextField()
    offer = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Price(models.Model):
    class Meta:
        ordering = ('id',)

    CHOICES = [
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
        ('Extra Large', 'Extra Large'),
    ]

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='prices')
    size = models.CharField(max_length=20, null=True,
                            blank=True, choices=CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.price} - {self.size}'


class Availability(models.Model):
    class Meta:
        verbose_name_plural = 'Availability'
        ordering = ('-end_time',)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def convert_to_localtime(self, utctime):
        fmt = '%d/%m/%Y %H:%M'
        localtz = localtime(utctime)
        return localtz.strftime(fmt)

    def __str__(self):
        start_time = self.convert_to_localtime(self.start_time)
        end_time = self.convert_to_localtime(self.end_time)
        return f'{start_time} - {end_time}'


class AppointmentManager(models.Manager):
    def available_appointments(self):
        last_updated = localtime(now()) - timedelta(hours=2)
        self.filter(last_updated__lte=last_updated,
                    reserved=True, confirmed=False).delete()
        return self.filter(
            models.Q(confirmed=True)
            | models.Q(last_updated__gte=last_updated))


class Appointment(models.Model):
    class Meta:
        ordering = ('-end_time',)

    objects = AppointmentManager()
    order = models.ForeignKey('orders.Order', null=True, blank=True,
                              on_delete=models.CASCADE,
                              related_name='appointments')
    service = models.ForeignKey(Service, null=True, blank=True,
                                on_delete=models.SET_NULL,
                                related_name='appointments')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    comments = models.TextField(null=True, blank=True)
    reserved = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    task_id = models.CharField(max_length=50, null=True,
                               blank=True, editable=False)
    last_updated = models.DateTimeField(null=True, blank=True)

    def convert_to_localtime(self, utctime):
        fmt = '%d/%m/%Y %H:%M'
        localtz = localtime(utctime)
        return localtz.strftime(fmt)

    def __str__(self):
        start_time = self.convert_to_localtime(self.start_time)
        end_time = self.convert_to_localtime(self.end_time)
        return f'{start_time} - {end_time}'

    def schedule_reminder(self):
        from .tasks import send_sms_reminder
        appointment_time = localtime(self.start_time)
        reminder_time = appointment_time - timedelta(minutes=30)
        current_time = localtime(now())
        milli_to_wait = int(
            (reminder_time - current_time).total_seconds()) * 1000
        result = send_sms_reminder.send_with_options(
            args=(self.pk,),
            delay=milli_to_wait)
        return result.options['redis_message_id']

    def cancel_task(self):
        redis_client = redis.Redis.from_url(settings.REDIS_URL, db=0)
        redis_client.hdel("dramatiq:default.DQ.msgs", self.task_id)
        return

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.task_id:
            self.task_id = self.cancel_task()
        if self.confirmed:
            self.task_id = self.schedule_reminder()
        super().save(*args, **kwargs)
