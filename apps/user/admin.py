from django.contrib import admin

from .models import User, Currency

admin.site.register(User)
admin.site.register(Currency)