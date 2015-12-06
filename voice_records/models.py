from django.db import models
from subscriber.models import Consumer
# Create your models here.


class VoiceRecord(models.Model):
    caller = models.ForeignKey(Consumer)
    level1_voice_part1 = models.FileField("recorded voice1", upload_to="records", blank=True, null=True)
    level1_voice_part2 = models.FileField("recorded voice2", upload_to="records", blank=True, null=True)
    level1_voice_part3 = models.FileField("recorded voice3", upload_to="records", blank=True, null=True)
    level2 = models.FileField("recorded voice4", upload_to="records", blank=True, null=True)
    level3 = models.FileField("recorded voice5", upload_to="records", blank=True, null=True)
    transcribed = models.BooleanField(default=False)
    level = models.CharField(max_length=1, default=1)
    call_tracking_id = models.CharField(max_length=32, null=True, blank=True)
    purpose_choice = (
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )
    purpose = models.CharField(max_length=6, choices=purpose_choice)
    with_error = models.BooleanField(default=False)
    remarks = models.TextField(null=True, blank=True)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.caller


class VoiceReg(models.Model):
    caller = models.CharField(max_length=32)
    caller_type = models.CharField(max_length=32)
    tracking_id = models.CharField(max_length=32)
    registration_voice_name = models.FileField("voice", upload_to="records", blank=True, null=True)
    registration_voice_address = models.FileField("voice", upload_to="records", blank=True, null=True)
    registration_voice_age = models.FileField("voice", upload_to="records", blank=True, null=True)
    registration_voice_intro = models.FileField("voice", upload_to="records", blank=True, null=True)
    completed = models.BooleanField(default=False)
    with_error = models.BooleanField(default=False)
    remarks = models.TextField(null=True, blank=True)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.caller