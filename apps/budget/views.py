from django.db import connection
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from .models import Budget
from ..expense.models import ExpenseCategory
from ..user.models import User


@method_decorator(never_cache, name='dispatch')
class BudgetView(View):
    template_name = 'budget.html'

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return redirect('user:login')

        # 1. Fetch raw budget data using Stored Procedure
        with connection.cursor() as cursor:
            cursor.callproc('get_budgets', [user_id])
            budgets_from_proc = cursor.fetchall()

        # 2. Convert raw tuples to dictionaries and attach categories
        # This is the "Hybrid" approach: SP for main data, ORM for relationships
        formatted_budgets = []

        for row in budgets_from_proc:
            # Map the tuple indices to names based on your HTML structure
            # row[0]=id, row[1]=amount, row[2]=name, row[3]=period
            budget_id = row[0]

            # Fetch categories for this specific budget using Django ORM
            # .all() fetches the list of categories efficiently
            try:
                # We get the budget object just to access the M2M relationship
                budget_obj = Budget.objects.get(budget_id=budget_id)
                categories = budget_obj.category.all()
            except Budget.DoesNotExist:
                categories = []

            formatted_budgets.append({
                'id': row[0],
                'amount': row[1],
                'name': row[2],
                'period': row[3],
                'categories': categories,  # This is the list we need for the HTML
            })

        total_budget = sum((b['amount'] or 0) for b in formatted_budgets)
        active_budgets = len(formatted_budgets)

        context = {
            'budgets': formatted_budgets,  # Now passing the list of dicts
            'total_budget': total_budget,
            'active_budgets': active_budgets,
            'categories': ExpenseCategory.objects.filter(user=user)  # For the modal dropdown
        }

        return render(request, self.template_name, context)

    def post(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        name = request.POST.get('budget_name')
        amount = request.POST.get('budget_amount')
        budget_period = request.POST.get('budget_period_days')
        category_ids = request.POST.getlist('expense_categories')

        with connection.cursor() as cursor:
            cursor.callproc('add_budget', [name, amount, budget_period, user_id])

        if category_ids:
            # We need to find the budget we just created.
            # We filter by user and name, and order by '-budget_id' to get the newest one.
            new_budget = Budget.objects.filter(user_id=user_id, name=name).order_by('-budget_id').first()

            if new_budget:
                # The star (*) unpacks the list of IDs into arguments
                new_budget.category.add(*category_ids)

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
