from django.urls import path
from . import views

app_name = 'savings'

urlpatterns = [
    path('', views.SavingsIndexView.as_view(), name='index'),
    path('add-goal/', views.add_goal, name='add_goal'),
    path('add-saving/', views.add_saving, name='add_saving'),
    path('saving-history/', views.saving_history, name='saving_history'),
    path('delete-goal/', views.delete_goal, name='delete_goal'),
    path('edit-goal/', views.edit_goal, name='edit_goal'),
    path('edit-saving/', views.edit_saving, name='edit_saving'),
    path('delete-saving/', views.delete_saving, name='delete_saving'),
]