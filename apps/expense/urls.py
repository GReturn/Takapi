from django.urls import path
from . import views

app_name = 'expense'

urlpatterns = [
    # Main expense page at /expense/
    path('', views.index, name='index'),
]