from django.db import models

from apps.currency.models import Currency


# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    gender = models.CharField(max_length=11)
    age = models.IntegerField(default=0)
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT)

    def __str__(self):
        return self.first_name + " " + self.last_name