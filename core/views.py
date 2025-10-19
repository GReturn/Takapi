from django.shortcuts import render
from django.views import View


class IndexView(View):
    template_name = './index.html'

    def get(self, request):
        return render(request, self.template_name)

class LoginView(View):
    template_name = './templates/login.html'
    def get(self, request):
        return render(request, self.template_name)
