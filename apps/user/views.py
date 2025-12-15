from django.contrib.auth.hashers import check_password, make_password
from django.db import connection, DatabaseError
from django.db.models import Sum
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from apps.user.models import Currency, User
from apps.budget.models import Budget
from apps.expense.models import Expense
from apps.savings.models import Saving, SavingGoal
from apps.reminder.models import Reminder


class IndexView(View):
    template_name = 'home.html'

    def get(self, request):
        return render(request, self.template_name)


class PrivacyView(View):
    template_name = 'privacy.html'

    def get(self, request):
        return render(request, self.template_name)


class TermsView(View):
    template_name = 'terms.html'

    def get(self, request):
        return render(request, self.template_name)


class LogoutView(View):
    def get(self, request):
        request.session.flush()
        return redirect(reverse('user:login'))


class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        if 'user_id' in request.session:
            return redirect('user:dashboard')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            if check_password(password, user.password):
                request.session['user_id'] = user.user_id
                request.session.set_expiry(0)
                return redirect('user:dashboard')

        except User.DoesNotExist:
            user = None

        return render(request, self.template_name, {'msg': 'Incorrect Email or Password'})


class SignupView(View):
    template_name = 'signup.html'

    def get(self, request):
        currencies = Currency.objects.all()
        return render(request, self.template_name, {'currencies': currencies})

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        currency_id = request.POST.get('currency_id')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        currencies = Currency.objects.all()

        if password != confirm_password:
            return render(request, self.template_name, {
                'msg': 'Passwords do not match',
                'currencies': currencies
            })

        try:
            hashed_password = make_password(password)

            with connection.cursor() as cursor:
                cursor.callproc('create_user', [
                    first_name,
                    last_name,
                    email,
                    age,
                    gender,
                    currency_id,
                    hashed_password
                ])
                result = cursor.fetchall()
                if result[0][0] != 'User successfully registered':
                    err_msg = result[0][0]

                    return render(request, self.template_name, {
                        'msg': err_msg,
                        'currencies': currencies
                    })
            return redirect('user:login')


        except Exception as e:
            return render(request, self.template_name, {
                'msg': f'Error creating user: {str(e)}',
                'currencies': currencies
            })


@method_decorator(never_cache, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'user-profile.html'

    def dispatch(self, request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('user:login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.session.get('user_id')

        try:
            current_user = User.objects.get(user_id=user_id)
            context['user'] = current_user
            context['currencies'] = Currency.objects.all()
        except User.DoesNotExist:
            pass # If user ID is invalid, flush session in the next step (logic handled in dispatch usually)

        return context

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return redirect('user:login')

        action = request.POST.get('action')

        if action == 'update_info':
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Info updated successfully.')

        elif action == 'update_preferences':
            user.age = request.POST.get('age')
            user.gender = request.POST.get('gender')

            currency_id = request.POST.get('currency')
            if currency_id:
                try:
                    user.currency = Currency.objects.get(pk=currency_id)
                except Currency.DoesNotExist:
                    messages.error(request, 'Invalid currency selected.')

            user.save()
            messages.success(request, 'Preferences updated successfully.')

        elif action == 'change_password':
            current_password = request.POST.get('password')
            new_password = request.POST.get('new_password1')
            new_password_confirmation = request.POST.get('new_password2')

            if not check_password(current_password, user.password):
                messages.error(request, 'Incorrect current password.')
            elif new_password != new_password_confirmation:
                messages.error(request, 'Passwords do not match.')
            else:
                user.password = make_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')

        elif action == 'delete_account':
            user.delete()
            request.session.flush()
            messages.success(request, 'Account deleted successfully.')
            return redirect('login')

        return redirect('user:profile')


@method_decorator(never_cache, name='dispatch')
class DashboardView(View):
    template_name = 'dashboard.html'

    def get(self, request):
        # 1. Security: Ensure user is logged in via your custom session
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return redirect('user:login')

        # --- CALCULATIONS ---

        # A. Total Savings (Sum of all Saving records)
        total_savings = Saving.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

        # B. Monthly Budget vs Expenses
        # Note: Summing all budgets. You might want to filter by period in the future.
        total_budget = Budget.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

        # Calculate Remaining Budget
        remaining_budget = total_budget - total_expenses
        # Calculate Percentage for the progress bar (avoid division by zero)
        budget_percent = (total_expenses / total_budget * 100) if total_budget > 0 else 0

        # C. Pending Reminders Count
        pending_reminders_count = Reminder.objects.filter(user=user, status=False).count()

        # --- LISTS & COMPLEX DATA ---

        # D. Active Saving Goals (Need to calculate progress for each)
        goals = SavingGoal.objects.filter(user=user)
        goals_data = []
        for goal in goals:
            # How much saved for THIS specific goal?
            saved_amount = Saving.objects.filter(user=user, goal=goal).aggregate(Sum('amount'))['amount__sum'] or 0

            # Percentage
            percent = (saved_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0

            goals_data.append({
                'name': goal.name,
                'current': saved_amount,
                'target': goal.target_amount,
                'percent': min(percent, 100),  # Cap at 100% for CSS width
                'target_date': goal.target_date
            })

        # E. Recent Expenses (Last 5)
        # Note: Your Expense model doesn't have a 'date' field in the snippet you sent.
        # I am ordering by ID (newest created) as a fallback.
        recent_expenses = Expense.objects.filter(user=user).select_related('category').order_by('-expense_id')[:5]

        # F. Reminders List (Next 3 pending)
        upcoming_reminders = Reminder.objects.filter(user=user, status=False).order_by('date_time')[:3]

        context = {
            'user': user,
            'currency': user.currency,  # Access currency via Foreign Key
            'total_savings': total_savings,
            'total_budget': total_budget,
            'total_expenses': total_expenses,
            'remaining_budget': remaining_budget,
            'budget_percent': budget_percent,
            'pending_count': pending_reminders_count,
            'goals_data': goals_data,
            'recent_expenses': recent_expenses,
            'upcoming_reminders': upcoming_reminders,
        }

        return render(request, self.template_name, context)