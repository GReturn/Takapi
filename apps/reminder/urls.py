from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReminderViewPage.as_view(), name="view"),
    path('create', views.CreateReminderPage.as_view(), name="create"),
]