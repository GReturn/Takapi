from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from .models import Budget
from ..user.models import User


@method_decorator(never_cache, name='dispatch')
class BudgetView(View):
    template_name = 'budget.html'

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        user = User.objects.get(user_id=user_id)
        budgets = Budget.objects.filter(user=user)

        context = {'budgets': budgets, 'user': user}

        return render(request, self.template_name, context)



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
