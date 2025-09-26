from django.db import models

# Create your models here.
class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    currency_short_name = models.CharField(max_length=11)
    currency_long_name = models.CharField(max_length=50)

    def __str__(self):
        return self.currency_short_name + " " + self.currency_long_name