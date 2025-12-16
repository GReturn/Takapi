from datetime import datetime

from django.db import connection
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from apps.reminder.models import Reminder
from apps.user.models import User


@method_decorator(never_cache, name='dispatch')
class ReminderIndexView(View):
    template_name = 'index.html'

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        user = User.objects.get(user_id=user_id)
        reminders = Reminder.objects.filter(user=user)

        context = {'user': user, 'reminders': reminders}

        return render(request, self.template_name, context)


class CreateReminderView(View):
    def post(self, request):
        # Logic to create reminder from POST data
        message = request.POST['message']
        description = request.POST['description']
        # Combine date + time into datetime
        date_time = datetime.strptime(f'{request.POST['date']} {request.POST['time']}', "%Y-%m-%d %H:%M")
        #session info
        user_id = request.session['user_id']
        p_out_message = ""
        # Save to DB
        with connection.cursor() as cursor:
            cursor.callproc("create_reminder", [user_id, message, date_time, description, p_out_message])
            cursor.execute("SELECT @_create_reminder_4;")
            message = cursor.fetchone()[0]
        print(message)
        return redirect('reminder:index')







