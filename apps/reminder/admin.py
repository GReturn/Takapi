from django.contrib import admin

from apps.reminder.models import Reminder, ReminderResponse

# Register your models here.
admin.register(Reminder)
admin.register(ReminderResponse)