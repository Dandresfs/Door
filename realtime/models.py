from __future__ import unicode_literals

from django.db import models
from Door.settings.base import STATIC_URL

# Create your models here.

class Employee(models.Model):
    card_id = models.CharField(max_length=100,unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    cedula = models.CharField(max_length=100)
    rh = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    photo = models.FileField(upload_to="Photos/",blank=True,null=True)

    def get_photo(self):
        photo = self.photo
        if photo.name == '':
            avatar = str(STATIC_URL+"img/logo.png")
        else:
            avatar = photo.url
        return avatar