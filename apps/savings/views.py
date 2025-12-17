from django.db import transaction, connection, DatabaseError
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.contrib import messages


from apps.savings.models import SavingGoal, Saving
from apps.user.models import User


def add_goal(request):
    if request.method != 'POST':
        return redirect('savings:index')

    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user:login')

    goal_name = request.POST.get('goal_name')
    target_amount = request.POST.get('target_amount')
    target_date = request.POST.get('target_date')

    if not goal_name or not target_amount or not target_date:
        return redirect('savings:index')

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.callproc(
                'add_saving_goal',
                [user_id, goal_name, target_amount, target_date]
            )

    return redirect('savings:index')
#
def add_saving(request):
    if request.method != 'POST':
        return redirect('savings:index')

    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user:login')

    goal_id = request.POST.get('goal_id')
    amount = request.POST.get('amount')

    # Basic validation
    if not goal_id or not amount:
        return redirect('savings:index')

    # Execute the simple stored procedure
    with connection.cursor() as cursor:
        cursor.callproc('add_saving', [user_id, goal_id, amount])

    return redirect('savings:index')
#
@never_cache
def saving_history(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user:login')

    user = User.objects.get(user_id=user_id)

    goal_filter = request.GET.get('goal_id')
    sort_field = request.GET.get('sort_field', 'date')
    sort_order = request.GET.get('sort_order', 'desc')

    goal_id = int(goal_filter) if goal_filter else None

    with connection.cursor() as cursor:
        if goal_id:
            cursor.callproc('get_saving_history_filtered', [user_id, goal_id, sort_field, sort_order])
        else:
            cursor.callproc('get_saving_history_filtered', [user_id, None, sort_field, sort_order])
        savings = cursor.fetchall()
        cursor.nextset()
        cursor.callproc('get_user_saving_goals', [user_id])
        goals = cursor.fetchall()
    total_saved = sum([row[1] for row in savings]) if savings else 0

    context = {
        'user': user,
        'savings': savings,
        'total_saved': total_saved,
        'goals': goals,
        'selected_goal': goal_filter,
        'sort_field': sort_field,
        'sort_order': sort_order
    }
    return render(request, 'savings/history.html', context)


def delete_goal(request):
    if request.method != 'POST':
        return redirect('savings:index')

    goal_id = request.POST.get('goal_id')
    target_goal_id = request.POST.get('target_goal_id') or None

    if target_goal_id == goal_id:
        target_goal_id = None

    try:
        with connection.cursor() as cursor:
            cursor.callproc('delete_goal_with_transfer', [goal_id, target_goal_id])
        messages.success(request, "Goal deleted successfully.")
    except DatabaseError as e:
        messages.error(request, "Action Failed: " + str(e))

    return redirect('savings:index')


def edit_goal(request):
    if request.method != 'POST':
        return redirect('savings:index')

    goal_id = request.POST.get('goal_id')
    name = request.POST.get('goal_name')
    target_amount = request.POST.get('target_amount')
    target_date = request.POST.get('target_date')

    # Basic validation
    if not goal_id or not name or not target_amount or not target_date:
        messages.error(request, "All fields are required.")
        return redirect('savings:index')

    try:
        with connection.cursor() as cursor:
            cursor.callproc('update_saving_goal', [
                goal_id,
                name,
                target_amount,
                target_date
            ])
        messages.success(request, "Goal updated successfully.")

    except DatabaseError as e:
        messages.error(request, "Failed to update goal. Please try again.")

    return redirect('savings:index')


def edit_saving(request):
    if request.method == 'POST':
        saving_id = request.POST.get('saving_id')
        amount = request.POST.get('amount')
        date = request.POST.get('date')

        with connection.cursor() as cursor:
            cursor.callproc('update_saving', [saving_id, amount, date])

        messages.success(request, "Transaction updated.")
    return redirect('savings:saving_history')


def delete_saving(request):
    if request.method == 'POST':
        saving_id = request.POST.get('saving_id')

        with connection.cursor() as cursor:
            cursor.callproc('delete_saving', [saving_id])

        messages.success(request, "Transaction deleted.")
    return redirect('savings:saving_history')

@method_decorator(never_cache, name='dispatch')
class SavingsIndexView(View):
    template_name = 'savings/index.html'

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        user = User.objects.get(user_id=user_id)
        goals_query = SavingGoal.objects.filter(user=user)

        goals_data = []
        for goal in goals_query:
            current = Saving.objects.filter(goal=goal).aggregate(Sum('amount'))['amount__sum'] or 0
            percent = (current / goal.target_amount * 100) if goal.target_amount > 0 else 0

            goals_data.append({
                'saving_goal_id': goal.saving_goal_id,
                'name': goal.name,
                'target_amount': goal.target_amount,
                'target_date': goal.target_date,
                'current_amount': current,
                'percent': percent
            })

        recent_savings = Saving.objects.filter(user=user).select_related('goal').order_by('-date', '-saving_id')[:10]

        total_saved = Saving.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

        context = {
            'user': user,
            'goals': goals_data,
            'recent_savings': recent_savings,
            'total_saved': total_saved
        }
        return render(request, self.template_name, context)