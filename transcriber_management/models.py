from django.db import models
from voice_records.models import VoiceRecord
# Create your models here.


class Transcriber(models.Model):
    name = models.CharField(max_length=32)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.name


class TranscriberInTranscription(models.Model):
    name = models.ForeignKey(Transcriber, related_name='who_transcribed')
    number_of_products = models.IntegerField()
    callID = models.ForeignKey(VoiceRecord, related_name='the_voice_call_transcribed')
    time_taken = models.CharField(max_length=32)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.name


class FailedTranscription(models.Model):
    name = models.ForeignKey(Transcriber, related_name='who_failed_to_transcribe')

    callID = models.ForeignKey(VoiceRecord, related_name='the_voice_call_failed_to_be_transcribed')
    remarks = models.CharField(max_length=128)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.name
