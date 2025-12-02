from django.shortcuts import render, redirect
from django.views import View

from apps.reminder.models import Reminder
from apps.user.models import User


class ReminderIndexView(View):
    template_name = 'reminder/index.html'

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        user = User.objects.get(user_id=user_id)
        reminders = Reminder.objects.filter(user=user)

        context = {'user': user, 'reminders': reminders}

        return render(request, 'index.html', context)


class CreateReminderView(View):
    def post(self, request):
        # Logic to create reminder from POST data
        # Combine date + time into datetime
        # Save to DB
        return redirect('reminder:index')

# ... Edit and Delete views similarly ...