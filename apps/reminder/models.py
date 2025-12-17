from django.db import models

from ..user.models import User
# Create your models here.

class Reminder(models.Model):
    reminder_id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=150, null=False)
    date_time = models.DateTimeField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(null=True)
    description = models.CharField(max_length=150, null=False, default="")
    date_responded = models.DateTimeField(null=True)

    def __str__(self):
        return f"Reminder #{self.reminder_id}"