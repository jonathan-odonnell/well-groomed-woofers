from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from .models import Availability, Appointment
from datetime import datetime, timedelta


@receiver(pre_save, sender=Availability)
@receiver(pre_delete, sender=Availability)
def delete_appointments_on_save(sender, instance, **kwargs):
    """
    Deletes appointments on availability create/update
    """
    try:
        availability = Availability.objects.get(id=instance.id)
        Appointment.objects.get(
            start_time__gte=availability.end_time,
            end_time__lte=availability.end_time,
            order=None
        ).delete()
    except Availability.DoesNotExist:
        pass


@receiver(post_save, sender=Availability)
def add_appointments_on_save(sender, instance, **kwargs):
    """
    Generates appointments on availability create/update
    """
    appointments = ['10:00', '13:00', '15:00']
    time_delta = instance.end_time - instance.start_time

    for i in range(time_delta.days + 1):
        date = instance.start_time.date() + timedelta(days=i)
        for appointment in appointments:
            start_time = datetime.combine(date, datetime.strptime(
                appointment, '%H:%M').time())
            end_time = datetime.combine(date, datetime.strptime(
                appointment, '%H:%M').time()) + timedelta(hours=2)
            Appointment.objects.get_or_create(
                start_time=start_time, end_time=end_time)


@receiver(post_save, sender=Appointment)
def update_appointment_on_save(sender, instance, **kwargs):
    """
    Update appointment task id on update
    """
    if instance.task_id:
        instance.task_id = instance.cancel_task()

    if instance.confirmed:
        instance.task_id = instance.schedule_reminder()
