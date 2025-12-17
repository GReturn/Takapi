from django.db import connection
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import Budget
from ..user.models import User
from apps.expense.models import ExpenseCategory, Expense  # Ensure Expense is imported


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

        # 1. Fetch raw budget data (Stored Procedure)
        with connection.cursor() as cursor:
            cursor.callproc('get_budgets', [user_id])
            budgets_from_proc = cursor.fetchall()

        formatted_budgets = []

        # Summary Variables
        total_allocated = 0
        total_spent_global = 0
        stats = {
            'on_track': 0,  # < 80%
            'near_limit': 0,  # 80% - 100%
            'over_budget': 0  # > 100%
        }

        # 2. Process each budget
        for row in budgets_from_proc:
            budget_id = row[0]
            budget_amount = row[1] or 0

            try:
                # Get the object to access Many-to-Many and created_at
                budget_obj = Budget.objects.get(budget_id=budget_id)
                categories = budget_obj.category.all()

                # --- CALCULATION LOGIC ---
                # 1. Get the start date (convert to date object to include all expenses from day 1)
                start_date = budget_obj.created_at.date()

                # 2. Calculate end date
                end_date = start_date + timedelta(days=budget_obj.budget_period)

                # 3. Sum expenses
                spent = Expense.objects.filter(
                    user=user,
                    category__in=categories,
                    date__gte=start_date,  # Now comparing Date vs Date (Safe!)
                    date__lte=end_date
                ).aggregate(Sum('amount'))['amount__sum'] or 0

            except Budget.DoesNotExist:
                categories = []
                spent = 0

            # Calculate Stats
            remaining = float(budget_amount) - float(spent)
            percentage = (float(spent) / float(budget_amount) * 100) if budget_amount > 0 else 0

            # Determine Status for Quick Stats
            if percentage > 100:
                status_color = 'red'
                stats['over_budget'] += 1
            elif percentage >= 80:
                status_color = 'yellow'
                stats['near_limit'] += 1
            else:
                status_color = 'green'
                stats['on_track'] += 1

            # Update Global Totals
            total_allocated += float(budget_amount)
            total_spent_global += float(spent)

            formatted_budgets.append({
                'id': row[0],
                'amount': budget_amount,
                'name': row[2],
                'period': row[3],
                'categories': categories,
                # New calculated fields
                'spent': spent,
                'remaining': remaining,
                'percentage': min(int(percentage), 100),  # Cap visual bar at 100%
                'real_percentage': int(percentage),  # Actual % for text
                'status_color': status_color
            })

        # Final Global Calc
        total_utilization = (total_spent_global / total_allocated * 100) if total_allocated > 0 else 0

        context = {
            'budgets': formatted_budgets,
            'categories': ExpenseCategory.objects.filter(user=user),
            # Summary Data
            'total_budget': total_allocated,
            'active_budgets': len(formatted_budgets),
            'total_utilization': int(total_utilization),
            'stats': stats,
            'total_spent': total_allocated - total_spent_global,
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

        # 1. Capture the selected category IDs for editing
        # Note: We use a different name 'edit_expense_categories' to distinguish from the create form
        category_ids = request.POST.getlist('edit_expense_categories')

        # 2. Update main fields using Stored Procedure
        with connection.cursor() as cursor:
            cursor.callproc('edit_budget', [budget_id, name, amount, period_days, user_id])

        # 3. Update Categories using Django ORM
        # We fetch the budget object and use .set() which automatically handles
        # clearing old categories and adding the new ones.
        try:
            budget = Budget.objects.get(budget_id=budget_id)
            budget.category.set(category_ids)
        except Budget.DoesNotExist:
            pass

        return redirect('budget:index')


class DeleteBudgetHardView(View):
    def post(self, request, budget_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        # 1. CLEANUP: Remove the Category links first (Django ORM)
        # This deletes the rows in the hidden "budget_budget_category" table
        # so the Foreign Key constraint doesn't block the SP.
        try:
            budget = Budget.objects.get(budget_id=budget_id)
            budget.category.clear()  # Removes all M2M associations
        except Budget.DoesNotExist:
            # If the budget doesn't exist, we can just proceed or return
            pass

        # 2. DELETE: Remove the Budget record (Stored Procedure)
        with connection.cursor() as cursor:
            cursor.callproc('delete_budget', [budget_id, user_id])

        return redirect('budget:index')
