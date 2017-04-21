from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Employee(models.Model):
    card_id = models.CharField(max_length=100,unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    status = models.CharField(max_length=100)