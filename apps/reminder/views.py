from django.shortcuts import render, redirect
from django.views import View

from apps.reminder.models import Reminder

# class ReminderViewPage(View):
#     template_name = "view-reminder-tw.html"
#
#     def get(self, request):
#         return render(request, self.template_name)
#
# class CreateReminderPage(View):
#     template_name = "create-reminder-tw.html"
#
#     def get(self, request):
#         return render(request, self.template_name)
#
# class EditReminderPage(View):
#     template_name = "edit-reminder-tw.html"
#
#     def get(self, request):
#         return render(request, self.template_name)


class ReminderIndexView(View):
    def get(self, request):
        # Fetch reminders for the logged-in user
        user_id = request.session.get('user_id')
        reminders = Reminder.objects.filter(user_id=user_id).order_by('date_time')

        return render(request, 'index.html', {'reminders': reminders})


class CreateReminderView(View):
    def post(self, request):
        # Logic to create reminder from POST data
        # Combine date + time into datetime
        # Save to DB
        return redirect('reminder:index')

# ... Edit and Delete views similarly ...