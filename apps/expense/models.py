from django.db import models
from django.utils import timezone

from apps.user.models import User


# Create your models here.
class ExpenseCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Expense(models.Model):
    expense_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.RESTRICT)
    description = models.CharField(max_length=255, default="")

    # Example: 1200.00 - Food
    def __str__(self):
        return f"{self.amount} - {self.category.name}"
