from django.db import connection
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

    # def get(self, request):
    #     user_id = request.session.get('user_id')
    #     if not user_id:
    #         return redirect('user:login')
    #
    #     user = User.objects.get(user_id=user_id)
    #     budgets = Budget.objects.filter(user=user)
    #
    #     context = {'budgets': budgets, 'user': user}
    #
    #     return render(request, self.template_name, context)

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return redirect('user:login')

        # Call the stored procedure
        with connection.cursor() as cursor:
            cursor.callproc('get_budgets', [user_id])
            budgets_from_proc = cursor.fetchall()

        context = {
            'budgets': budgets_from_proc,
            'user': user
        }

        return render(request, self.template_name, context)

    def post(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        name = request.POST.get('budget_name')
        amount = request.POST.get('budget_amount')
        budget_period = request.POST.get('budget_period_days')

        with connection.cursor() as cursor:
            cursor.callproc('add_budget', [name, amount, budget_period, user_id])

        return redirect('budget:index')


class EditBudgetView(View):
    def post(self, request, budget_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        name = request.POST.get('edit_name')
        amount = request.POST.get('edit_amount')
        period_days = request.POST.get('edit_period_days')

        with connection.cursor() as cursor:
            cursor.callproc('edit_budget', [budget_id, name, amount, period_days, user_id])

        return redirect('budget:index')


class DeleteBudgetHardView(View):
    def post(self, request, budget_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        with connection.cursor() as cursor:
            cursor.callproc('delete_budget', [budget_id, user_id])

        return redirect('budget:index')
