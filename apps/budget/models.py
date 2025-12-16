from django.db import models

from apps.expense.models import ExpenseCategory
from apps.user.models import User


# Create your models here.
class Budget(models.Model):
    budget_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    name = models.CharField(max_length=100)
    budget_period = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ManyToManyField(ExpenseCategory, blank=True, related_name='budgets')

    def __str__(self):
        return self.name
