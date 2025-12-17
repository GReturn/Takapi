from django.urls import path
from . import views
from .views import EditBudgetView, DeleteBudgetHardView

app_name = 'budget'

urlpatterns = [
    path('', views.BudgetView.as_view(), name='index'),
    path('edit/<int:budget_id>/', EditBudgetView.as_view(), name='edit_budget'),
    path('delete/<int:budget_id>/', DeleteBudgetHardView.as_view(), name='delete_budget')
]
