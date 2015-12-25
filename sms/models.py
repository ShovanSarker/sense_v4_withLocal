from django.db import models
from subscriber.models import Consumer

# Create your models here.


class SMSPayment(models.Model):
    buyer = models.ForeignKey(Consumer, related_name='buyer_receiving_payment')
    seller = models.ForeignKey(Consumer, related_name='seller_receiving_payment')
    amount = models.FloatField()
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.buyer
