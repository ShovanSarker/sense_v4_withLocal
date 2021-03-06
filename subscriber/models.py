from django.db import models
# Create your models here.


class ConsumerType(models.Model):
    type_name = models.CharField(max_length=16)
    remarks = models.CharField(max_length=64, null=True, blank=True)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.type_name


class Consumer(models.Model):
    name = models.CharField(max_length=64)
    type = models.ForeignKey(ConsumerType)
    phone = models.CharField(max_length=32)
    address = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    age = models.FloatField(null=True, blank=True)
    married = models.BooleanField(default=False)
    number_of_child = models.CharField(null=True, blank=True, max_length=255)
    gender_choice = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('None', 'None'),
    )
    gender = models.CharField(max_length=6, choices=gender_choice)
    user_level = models.IntegerField(default=1)
    total_successful_call = models.IntegerField(default=0)
    number_of_calls_with_error = models.IntegerField(default=0)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.name


class Connectivity(models.Model):
    user = models.ForeignKey(Consumer, related_name='who_called')
    introduced_by = models.ForeignKey(Consumer, related_name='introduced_by')
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.user


class Recharge(models.Model):
    user = models.ForeignKey(Consumer, related_name='who_was_recharged')
    amount = models.FloatField(default=0)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.user


class TotalRecharge(models.Model):
    user = models.ForeignKey(Consumer, related_name='who_was_total_recharged')
    amount = models.FloatField(default=0)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.user


class ACL(models.Model):
    loginID = models.CharField(max_length=9)
    loginUser = models.ForeignKey(Consumer, related_name='who_logging_in')
    distUser = models.ForeignKey(Consumer, related_name='who_is_the_boss', null=True, blank=True)

    def __unicode__(self):
        return self.loginID
