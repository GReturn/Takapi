from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.views import View
from apps.expense.models import Expense
from apps.user.models import User
from django.db import connection
from datetime import date

# Expense View -> 
@method_decorator(never_cache, name='dispatch')
class ExpenseView(View):
    template_name = 'expense/index.html'

    # Get User Expenses -> sp_get_user_expenses
    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        user = User.objects.get(user_id=user_id)
        user_expenses = []
        with connection.cursor() as cursor:
            cursor.callproc('sp_get_user_expenses', [user_id])
            columns = [col[0] for col in cursor.description]
            user_expenses = [dict(zip(columns, row)) for row in cursor.fetchall()]

        largest_expense_val = 0

        # Get Largest Expense
        if user_expenses:
            largest_expense_val = max([e['amount'] for e in user_expenses])
            largest_expense_val = f"{largest_expense_val:,.2f}"

        # Get Expenses By Category -> sp_expenses_by_category
        categories = []
        with connection.cursor() as cursor:
            cursor.callproc('sp_expenses_by_category', [user_id])
            columns = [col[0] for col in cursor.description]
            categories = [dict(zip(columns, row)) for row in cursor.fetchall()]

        colors = [
            '#EF4444', '#3B82F6', '#10B981', '#F59E0B', '#6366F1', '#8B5CF6', '#EC4899', '#14B8A6',
            '#F97316', '#06B6D4', '#84CC16', '#A855F7', '#EF4444', '#0EA5E9', '#22C55E', '#F59E0B'
        ]
        
        name_to_color = {}
        for cat in categories:
            color_index = cat['category_id'] % len(colors)
            cat['color'] = colors[color_index]
            cat['dot_attr'] = f'style="background-color: {cat["color"]}"'
            name_to_color[cat['category_name']] = cat['color']
            
        for expense in user_expenses:
            if 'category_id' in expense:
                 expense['color'] = colors[expense['category_id'] % len(colors)]
            elif 'category_name' in expense and expense['category_name'] in name_to_color:
                 expense['color'] = name_to_color[expense['category_name']]
            else:
                expense['color'] = '#9CA3AF'
            
            # Format amount with commas
            if 'amount' in expense:
                expense['amount_formatted'] = f"{expense['amount']:,.2f}"

            c = expense['color']
            expense['badge_attr'] = f'style="background-color: {c}15; color: {c}; border-color: {c}30;"'
        
        monthly_summary = {}
        today = date.today()
        # Monthly Summary -> sp_monthly_summary
        with connection.cursor() as cursor:
            cursor.callproc('sp_monthly_summary', [user_id, today.year, today.month])
            columns = [col[0] for col in cursor.description]
            result = cursor.fetchone()
            if result:
                monthly_summary = dict(zip(columns, result))
                if 'total_spent' in monthly_summary and monthly_summary['total_spent']:
                     monthly_summary['total_spent'] = f"{monthly_summary['total_spent']:,.2f}"
        
        monthly_summary['largest_expense'] = largest_expense_val

        context = {
            'expenses': user_expenses,
            'kpi': monthly_summary,
            'categories': categories,
            'user': user
        }
        return render(request, self.template_name, context)


# Add Expense -> sp_add_expense
@method_decorator(never_cache, name='dispatch')
class AddExpenseView(View):
    def post(self, request):
        user_id = request.session.get('user_id')
        expense_id = request.POST.get('expense_id')
        
        amount = request.POST.get('amount')
        expense_date = request.POST.get('date')
        category_id = request.POST.get('category')
        description = request.POST.get('description')

        with connection.cursor() as cursor:
            if expense_id:
                # Update Expense -> sp_update_expense
                cursor.callproc('sp_update_expense', [expense_id, amount, expense_date, category_id, description])
                messages.success(request, 'Expense updated successfully!')
            else:
                # Add Expense -> sp_add_expense
                cursor.callproc('sp_add_expense', [amount, expense_date, user_id, category_id, description])
                messages.success(request, 'Expense added successfully!')
        
        return redirect('expense:index')


# Delete Expense -> sp_delete_expense
@method_decorator(never_cache, name='dispatch')
class DeleteExpenseView(View):
    def post(self, request, expense_id):
        user_id = request.session.get('user_id')
        with connection.cursor() as cursor:
            # Delete Expense -> sp_delete_expense
            cursor.callproc('sp_delete_expense', [expense_id, user_id])
        
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense:index')


# Add Category -> sp_add_category
@method_decorator(never_cache, name='dispatch')
class AddCategoryView(View):
    def post(self, request):
        user_id = request.session.get('user_id')
        name = request.POST.get('name')
        category_id = request.POST.get('category_id')
        
        with connection.cursor() as cursor:
            if category_id:
                # Update Category -> sp_update_category
                cursor.callproc('sp_update_category', [category_id, name, user_id])
                messages.success(request, f'Category renamed to "{name}" successfully!')
            else:
                # Add Category -> sp_add_category
                cursor.callproc('sp_add_category', [name, user_id])
                result = cursor.fetchone()
                if result and result[0] == -1:
                     messages.error(request, f'Category "{name}" already exists.')
                else:
                     messages.success(request, f'Category "{name}" created successfully!')

        return redirect('expense:index')




# Delete Category -> sp_delete_category
@method_decorator(never_cache, name='dispatch')
class DeleteCategoryView(View):
    def post(self, request, category_id):
        user_id = request.session.get('user_id')
        try:
            with connection.cursor() as cursor:
                # Delete Category -> sp_delete_category
                cursor.callproc('sp_delete_category', [category_id, user_id])
                result = cursor.fetchone()
                
                if result and result[0] == -1:
                    messages.error(request, 'Cannot delete category: It still has expenses. Please delete or reassign them first.')
                else:
                    messages.success(request, 'Category deleted successfully!')
                    
        except Exception as e:
            messages.error(request, 'Cannot delete category: It still has expenses linked to it.')
            
        return redirect('expense:index')
