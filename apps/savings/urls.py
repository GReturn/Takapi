from django.urls import path
from . import views

app_name = 'savings'

urlpatterns = [
    path('', views.SavingsIndexView.as_view(), name='index'),
    path('add-goal/', views.add_goal, name='add_goal'),
    path('add-saving/', views.add_saving, name='add_saving'),
    path('saving-history/', views.saving_history, name='saving_history'),
]