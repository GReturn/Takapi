from django.db import models

class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    currency_short_name = models.CharField(max_length=11)
    currency_long_name = models.CharField(max_length=50)

    def __str__(self):
        return self.currency_short_name + " " + self.currency_long_name

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