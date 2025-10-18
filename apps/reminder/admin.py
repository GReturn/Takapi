from django.contrib import admin

from .models import Reminder
# , ReminderResponse

# Register your models here.
admin.site.register(Reminder)
# admin.site.register(ReminderResponse)