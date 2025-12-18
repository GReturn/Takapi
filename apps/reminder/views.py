from datetime import datetime

from django.contrib import messages
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
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                return redirect('user:login')

            with connection.cursor() as cursor:
                cursor.callproc("update_reminder_status", [user_id])

            user = User.objects.get(user_id=user_id)
            reminders = Reminder.objects.filter(user=user)

            context = {'user': user, 'reminders': reminders}
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

        return render(request, self.template_name)


    def post(self, request):
        try:
            user_id = request.session.get('user_id')
            filter_option = request.POST.get('filter-options')
            if not user_id:
                return redirect('user:login')

            with connection.cursor() as cursor:
                cursor.callproc("update_reminder_status", [user_id])

            user = User.objects.get(user_id=user_id)
            if filter_option == "None":
                reminders = Reminder.objects.filter(user=user)
                context = {'user': user, 'reminders': reminders}
            else:
                filters=["Pending", "Completed", "Overdue"]
                filter_equivalence=[None, True, False]

                status_filter = filter_equivalence[filters.index(filter_option)]
                reminders = Reminder.objects.filter(user=user, status=status_filter)
                context = {'user': user, 'reminders': reminders, 'filters':filter_option}
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

        return render(request, self.template_name)


class CreateReminderView(View):
    def post(self, request):
        try:
            message = request.POST.get('message')
            description = request.POST.get('description')
            date_time = datetime.strptime(f"{request.POST.get('date')} {request.POST.get('time')}", "%Y-%m-%d %H:%M")
            user_id = request.session.get('user_id')
            if not user_id:
                return redirect('user:login')
            p_out_message = ""
            with connection.cursor() as cursor:
                cursor.callproc("create_reminder", [user_id, message, date_time, description, p_out_message])
                cursor.execute("SELECT @_create_reminder_4;")
                message = cursor.fetchone()[0]
            print(message)
            if message == "Successfully created a new reminder":
                messages.success(request, message)
            else:
                messages.error(request, message)
        except Exception as e:
            messages.error(request, f'An error occurred when creating the reminder: {e}')
        
        return redirect('reminder:index')

class DeleteReminderView(View):
    def post(self, request, reminder_id):
        try:
            user_id = request.session.get("user_id")
            if not user_id:
                return redirect('user:login')
            p_out_message = ""
            with connection.cursor() as cursor:
                cursor.callproc("delete_reminder", [reminder_id, user_id, p_out_message])
                cursor.execute("SELECT @_delete_reminder_2;")
                message = cursor.fetchone()[0]
            if message == "Successfully deleted":
                messages.success(request, message)
            else:
                messages.error(request, message)
        except Exception as e:
            messages.error(request, f'An error occurred when deleting the reminder: {e}')

        return redirect('reminder:index')

class EditReminderView(View):
    def post(self, request, reminder_id):
        try:
            message = request.POST.get('message')
            description = request.POST.get('description')
            date_time = datetime.strptime(f"{request.POST.get('date')} {request.POST.get('time')}", "%Y-%m-%d %H:%M")
            user_id = request.session.get('user_id')
            if not user_id:
                return redirect('user:login')
            p_out_msg = ""
            with connection.cursor() as cursor:
                cursor.callproc("update_reminder", [reminder_id, user_id, message, date_time, description, p_out_msg])
                cursor.execute("SELECT @_update_reminder_5;")
                message = cursor.fetchone()[0]
            if message == "Successfully updated":
                messages.success(request, message)
            else:
                messages.error(request, message)
        except Exception as e:
            messages.error(request, f'An error occurred when updating the reminder: {e}')
        return redirect('reminder:index')

class CompleteReminderView(View):
    def post(self, request, reminder_id):
        try:
            user_id = request.session.get("user_id")
            if not user_id:
                return redirect('user:login')
            p_out_msg = ""
            with connection.cursor() as cursor:
                cursor.callproc("complete_reminder", [reminder_id, user_id, p_out_msg])
                cursor.execute("SELECT @_complete_reminder_2;")
                message = cursor.fetchone()[0]
            if message == "Successfully marked as completed":
                messages.success(request, message)
            else:
                messages.error(request, message)
        except Exception as e:
            messages.error(request, f'An error occurred when completing the reminder: {e}')
        return redirect('reminder:index')






