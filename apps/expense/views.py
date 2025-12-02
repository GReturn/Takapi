from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from apps.expense.models import Expense
from apps.user.models import User


@method_decorator(never_cache, name='dispatch')
class ExpenseView(View):
    template_name = 'expense/index.html'

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user:login')

        user = User.objects.get(user_id=user_id)
        expenses = Expense.objects.filter(user=user)

        context = {'expenses': expenses, 'user': user}

        return render(request, self.template_name, context)