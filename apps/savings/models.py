from django.db import models
from apps.user.models import User


class SavingGoal(models.Model):
    saving_goal_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(decimal_places=2, max_digits=12)
    target_date = models.DateField()

    def __str__(self):
        return f"{self.name} - Target: {self.target_date}"


class Saving(models.Model):
    saving_id = models.AutoField(primary_key=True)
    goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} saved on {self.date} for {self.goal}"