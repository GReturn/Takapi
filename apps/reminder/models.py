from django.db import models

from ..user.models import User
# Create your models here.

class Reminder(models.Model):
    reminder_id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=150, null=False)
    date_time = models.DateTimeField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reminder #{self.reminder_id}"

class ReminderResponse(models.Model):
    response_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=150, null=False)
    date_responded = models.DateField(null=False)
    reminder = models.OneToOneField(Reminder, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Response #{self.response_id}"