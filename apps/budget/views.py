from django.contrib import messages
from django.db import connection, IntegrityError, DatabaseError
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.db.models import Sum
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

                start_date = budget_obj.created_at

                end_date = start_date + timedelta(days=budget_obj.budget_period)

                spent = Expense.objects.filter(
                    user=user,
                    category__in=categories,
                    date__gte=start_date,
                    date__lte=end_date
                ).aggregate(Sum('amount'))['amount__sum'] or 0
                print(f"Budget: {row[2]}, Start: {start_date}, Expense Sum: {spent}")
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

        if Budget.objects.filter(user_id=user_id, name=name).exists():
            messages.error(request, f"You already have a budget named '{name}'.")
            return redirect('budget:index')

        try:
            # 1. Try to Create Budget
            with connection.cursor() as cursor:
                cursor.callproc('add_budget', [name, amount, budget_period, user_id])

            # 2. Try to Link Categories
            if category_ids:
                new_budget = Budget.objects.filter(user_id=user_id, name=name).order_by('-budget_id').first()
                if new_budget:
                    new_budget.category.add(*category_ids)

            # If we get here, everything worked
            messages.success(request, f"Budget '{name}' created successfully!")

        except IntegrityError:
            # This catches duplicates if your DB has UNIQUE constraints
            messages.error(request, "A budget with this name might already exist.")
        except DatabaseError as e:
            # This catches generic DB errors (like Stored Procedure failures)
            messages.error(request, "Database error: Could not save budget.")
        except Exception as e:
            # This catches Python errors
            messages.error(request, f"Unexpected error: {str(e)}")

        return redirect('budget:index')


class EditBudgetView(View):
    def post(self, request, budget_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        name = request.POST.get('edit_name')
        amount = request.POST.get('edit_amount')
        period_days = request.POST.get('edit_period_days')
        category_ids = request.POST.getlist('edit_expense_categories')

        try:
            with connection.cursor() as cursor:
                cursor.callproc('edit_budget', [budget_id, name, amount, period_days, user_id])

            # Update Categories (Django ORM handles errors gracefully usually, but good to wrap)
            budget = Budget.objects.get(budget_id=budget_id)
            budget.category.set(category_ids)

            messages.success(request, "Budget updated successfully!")

        except Budget.DoesNotExist:
            messages.error(request, "Budget not found.")
        except Exception as e:
            messages.error(request, f"Error updating budget: {str(e)}")

        return redirect('budget:index')


class DeleteBudgetHardView(View):
    def post(self, request, budget_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        try:
            budget = Budget.objects.get(budget_id=budget_id)
            budget.category.clear()  # Removes all M2M associations
        except Budget.DoesNotExist:
            # If the budget doesn't exist, we can just proceed or return
            pass

        with connection.cursor() as cursor:
            cursor.callproc('delete_budget', [budget_id, user_id])

        return redirect('budget:index')
