from django.db import models

# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField()
    number = models.IntegerField()
    mentor_id = models.IntegerField(null=True, blank=True)                 # Employee ID in FastAPI (NOT a ForeignKey)
    mentor_name = models.CharField(max_length=100, null=True, blank=True)  # copy of the name taken from FastAPI