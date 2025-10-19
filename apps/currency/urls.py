from django.urls import path
from . import views

urlpatterns = [
    path('currency/', views.index, name='index'),
]