from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum

from apps.user.models import Currency, User
from apps.budget.models import Budget
from apps.expense.models import Expense
from apps.savings.models import Saving, SavingGoal
from apps.reminder.models import Reminder


class IndexView(View):
    template_name = 'index.html'

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


class LoginView(View):
    template_name = 'login.html'
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # --- THIS IS THE "ARBITRARY" LOGIN ---
        # It finds the first User in your database and logs them in
        # This is for development only!

        # 1. Get the first user from your custom User table
        user = User.objects.first()

        # 2. If no users exist, create one to log in with
        if not user:
            # Assuming you have at least one currency in your DB
            default_currency = Currency.objects.first()
            if not default_currency:
                default_currency = Currency.objects.create(
                    currency_short_name="USD",
                    currency_long_name="US Dollar"
                )

            user = User.objects.create(
                email="dev@example.com",
                first_name="Dev",
                last_name="User",
                gender="N/A",
                age=25,
                currency=default_currency
            )

        # 3. Store the user's ID in the session. This is how we "log them in".
        request.session['user_id'] = user.user_id

        # 4. Redirect to the profile page
        return redirect('dashboard')

class SignupView(View):
    template_name = 'signup.html'
    def get(self, request):
        return render(request, self.template_name)

class ProfileView(TemplateView):
    # Make sure this template name matches your file name!
    # You had 'user-profile.html' in your code, but 'profile.html' in our other conversation
    template_name = 'user-profile.html'

    # We add a 'dispatch' method to manually check for our login session
    def dispatch(self, request, *args, **kwargs):
        # If 'user_id' is NOT in the session, redirect to the login page
        if 'user_id' not in request.session:
            return redirect('login')

        # If it IS in the session, continue to the 'get' method
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Get the user_id we stored in the session
        user_id = self.request.session.get('user_id')

        # 2. Fetch the correct user from your custom User model
        try:
            current_user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            # If user was deleted, log them out and send to login
            # del request.session['user_id']
            return redirect('login')

        # 3. Pass the correct user object to the template
        context['user'] = current_user
        context['currencies'] = Currency.objects.all()

        return context


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    # 1. Protect the view: Check if user is "logged in" via session
    def dispatch(self, request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- DUMMY DATA (No Database Needed) ---

        # We create a simple dictionary to mimic the User model
        dummy_user = {
            'fname': 'Dev',
            'lname': 'User',
            'email': 'dev@example.com',
        }

        # We create a simple dictionary to mimic the Currency model
        dummy_currency = {
            'shortname': 'USD',
            'longname': 'US Dollar',
        }

        # Pass these to the template
        context['user'] = dummy_user
        context['currency'] = dummy_currency
        context['active_page'] = 'dashboard'

        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #
    #     # 2. Get the current user
    #     user_id = self.request.session.get('user_id')
    #     try:
    #         current_user = User.objects.get(user_id=user_id)
    #     except User.DoesNotExist:
    #         return redirect('login')
    #
    #     # 3. Currency Data
    #     # Accessing the currency object related to the user
    #     user_currency = current_user.currency
    #     currency_symbol = user_currency.currency_short_name if user_currency else "PHP"
    #
    #     # 4. DATA ANALYTICS / AGGREGATIONS
    #
    #     # A. Total Savings (Sum of all Saving records for this user)
    #     # We use 'aggregate' to sum the 'amount' column
    #     savings_data = Saving.objects.filter(user=current_user).aggregate(Sum('amount'))
    #     total_savings = savings_data['amount__sum'] or 0
    #
    #     # B. Total Expenses (Sum of all Expense records)
    #     expense_data = Expense.objects.filter(user=current_user).aggregate(Sum('amount'))
    #     total_expenses = expense_data['amount__sum'] or 0
    #
    #     # C. Budget Calculations
    #     # Get the most recent budget created by the user
    #     current_budget = Budget.objects.filter(user=current_user).last()
    #     budget_limit = current_budget.amount if current_budget else 0
    #
    #     # Simple math for the dashboard
    #     remaining_budget = budget_limit - total_expenses
    #     budget_percentage = 0
    #     if budget_limit > 0:
    #         budget_percentage = (total_expenses / budget_limit) * 100
    #
    #     # 5. Fetch Lists for the UI
    #
    #     # Get 5 most recent expenses, joining with 'category' to get the name
    #     # Note: Ensure your Expense model has a ForeignKey to 'category' with related_name or correct naming
    #     recent_expenses = Expense.objects.filter(user=current_user).select_related('category').order_by('-date')[:5]
    #
    #     # Get all saving goals
    #     saving_goals = SavingGoal.objects.filter(user=current_user)
    #
    #     # Get unread reminders
    #     reminders = Reminder.objects.filter(user=current_user, status='unread')
    #
    #     # 6. Pass everything to the template
    #     context.update({
    #         'user': current_user,
    #         'currency': user_currency,
    #         'currency_symbol': currency_symbol,
    #         'total_savings': total_savings,
    #         'total_expenses': total_expenses,
    #         'current_budget': current_budget,
    #         'remaining_budget': remaining_budget,
    #         'budget_percentage': budget_percentage,
    #         'recent_expenses': recent_expenses,
    #         'saving_goals': saving_goals,
    #         'reminders': reminders,
    #     })
    #
    #     return context