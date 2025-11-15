from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='budget_index'),
    path('create/', views.create_budget, name='create_budget'),
]