from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Budget
# Create your views here.

def index(request):

    return render(request, 'budget.html')

@login_required
def create_budget(request):
    if request.method == 'POST':
        Budget.objects.create(
            user=request.user,
            name=request.POST['name'],
            amount=request.POST['amount'],
            period_days=request.POST['period_days']
        )
        return redirect('budget:budget')
    return redirect('budget:budget')
