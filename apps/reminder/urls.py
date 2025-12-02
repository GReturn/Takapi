from django.urls import path
from . import views

app_name = 'reminder'

urlpatterns = [
    path('', views.ReminderViewPage.as_view(), name="index"),
    path('create', views.CreateReminderPage.as_view(), name="create"),
    path('edit', views.EditReminderPage.as_view(), name="edit"),
]