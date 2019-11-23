from django.db import models
from datetime import date
# Create your models here.

class Age(models.Model):
    age = models.CharField(max_length=32, blank=True, null=True,default=None)

class Users(models.Model):
    id = models.IntegerField(unique=True,primary_key=True)
    first_name = models.CharField(max_length=32, blank=True, null=True)
    last_name = models.CharField(max_length=32, blank=True, null=True)
    username = models.CharField(max_length=32, blank=True, null=True)
    role = models.IntegerField(default=1,blank=False,null=False)
    age = models.ForeignKey(Age, on_delete=models.CASCADE,default=None,null=True,blank=True)
    phone = models.CharField(max_length=32, blank=True, null=True)

class Level(models.Model):
    level = models.CharField(max_length=32, blank=True, null=True)

class Trial(models.Model):
    teacher = models.ForeignKey(Users, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, null=True)
    age = models.ForeignKey(Age, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

class TrialGroups(models.Model):
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE)
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

class Group(models.Model):
    teacher = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, blank=True, null=True)
    first_date = models.DateTimeField(blank=True, null=True)
    second_date = models.DateTimeField(blank=True, null=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE,null=True,blank=True)

    def today(self):
        if self.first_date.date == datetime.date():
            return True
        elif self.second_date.date == datetime.date():
            return True
        else:
            return False
    def info(self):
        return "Следующие занятия с преподавателем: {0}\n{1}\n{2}".format(self.teacher,self.first_date,self.second_date)

class Transactions(models.Model):
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    amount = models.IntegerField(blank=True,null=True)
    status = models.BooleanField(default=False)
    end_date = models.DateTimeField(blank=True, null=True)

class Students(models.Model):
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    payment =  models.ForeignKey(Transactions, on_delete=models.CASCADE,null=True,blank=True)

class StudentsMarks(models.Model):
    student = models.ForeignKey(Users, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    