from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

from django.shortcuts import render

def show_all_goals(request):
    return render(request, 'savings/show_all_goals.html')

def add_goal(request):
    return render(request, 'savings/add_goal.html')

def add_saving(request):
    return render(request, 'savings/add_saving.html')

def saving_history(request):
    return render(request, 'savings/saving_history.html')