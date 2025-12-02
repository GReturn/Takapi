from django.shortcuts import render, redirect
from django.views import View

from apps.reminder.models import Reminder
from apps.user.models import User


class ReminderIndexView(View):
    def get(self, request):
        # Fetch reminders for the logged-in user
        # user_id = request.session.get('user_id')
        user = User.objects.get(user_id=request.session['user_id'])
        reminders = Reminder.objects.filter(user_id=user.user_id).order_by('date_time')

        return render(request, 'index.html', {'reminders': reminders})


class CreateReminderView(View):
    def post(self, request):
        # Logic to create reminder from POST data
        # Combine date + time into datetime
        # Save to DB
        return redirect('reminder:index')

# ... Edit and Delete views similarly ...