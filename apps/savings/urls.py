from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_all_goals, name='show_all_goals'),
    path('add-goal/', views.add_goal, name='add_goal'),
    path('add-saving/', views.add_saving, name='add_saving'),
    path('saving-history/', views.saving_history, name='saving_history'),
]