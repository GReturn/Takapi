from django.db import models

from apps.user.models import User


# Create your models here.

class SavingGoal(models.Model):
    savinggoalid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    targetamount = models.DecimalField(decimal_places=2, max_digits=12)
    targetdate = models.DateField()

    def __str__(self):
        return f"{self.name} - Target: {self.targetdate}"


class Saving(models.Model):
    savingid = models.AutoField(primary_key=True)
    goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} saved on {self.date} for {self.goal}"