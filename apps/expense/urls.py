from django.urls import path
from . import views

app_name = 'expense'

urlpatterns = [
    path('', views.ExpenseView.as_view(), name='index'),
    path('add/', views.AddExpenseView.as_view(), name='add_expense'),
    path('delete/<int:expense_id>/', views.DeleteExpenseView.as_view(), name='delete_expense'),
    path('category/add/', views.AddCategoryView.as_view(), name='add_category'),
    path('category/delete/<int:category_id>/', views.DeleteCategoryView.as_view(), name='delete_category'),
]