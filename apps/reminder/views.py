from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views import View


# Create your views here.
class ReminderViewPage(View):
    template_name = "view-reminder.html"

    def get(self, request):
        return render(request, self.template_name)

class CreateReminderPage(View):
    template_name = "create-reminder.html"

    def get(self, request):
        return render(request, self.template_name)
