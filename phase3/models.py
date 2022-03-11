import sys

# from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    role = models.CharField(max_length=20)

    def __str__(self):
        return str(self.username)


class Cargo(models.Model):
    id = models.AutoField(primary_key=True)
    sender_name = models.CharField(max_length=20)
    recip_name = models.CharField(max_length=20)
    recip_address = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE, blank=True, null=True)
    Container = models.ForeignKey('Container', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Container(models.Model):
    cid = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    location_x = models.IntegerField(default=0)
    location_y = models.IntegerField(default=0)
    state = models.CharField(max_length=100)

    def __str__(self):
        return str(self.description)


class Tracker(models.Model):
    tid = models.AutoField(primary_key=True)
    tracker_description = models.CharField(max_length=100)
    top = models.IntegerField(default=sys.maxsize)
    left = models.IntegerField(default=-sys.maxsize)
    bottom = models.IntegerField(default=-sys.maxsize)
    right = models.IntegerField(default=sys.maxsize)
    tracker_owner = models.ForeignKey(MyUser, on_delete=models.CASCADE, blank=True, null=True)
    Container = models.ManyToManyField("Container")
    Cargo = models.ManyToManyField("Cargo")

    def __str__(self):
        return str(self.tracker_description)

