from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from apps.user.models import Currency, User


class IndexView(View):
    template_name = 'index.html'

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
        return redirect('profile')


# We removed LoginRequiredMixin
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