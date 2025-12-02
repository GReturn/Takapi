from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from apps.savings.models import SavingGoal, Saving
from apps.user.models import User


def add_goal(request):
    # handle functionalities here for adding goal
    pass
#
def add_saving(request):
    # handle functionalities
    pass
#
def saving_history(request):
    # handle functionalities
    pass


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