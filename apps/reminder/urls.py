from django.urls import path
from . import views

app_name = 'reminder'

urlpatterns = [
    path('', views.ReminderIndexView.as_view(), name="index"),
    path('create', views.CreateReminderView.as_view(), name="create"),
]