from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    """
    Main expense tracking page.
    Displays expense dashboard with summary and list of expenses.
    """
    return render(request, 'expense/index.html')
    # return HttpResponse("<h1>Hello from Expense App!</h1>")