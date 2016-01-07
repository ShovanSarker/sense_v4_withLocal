from django.db import models
from subscriber.models import Consumer
from product.models import Product
from voice_records.models import VoiceRecord
from transcriber_management.models import Transcriber
# Create your models here.


class BuyerSellerAccount(models.Model):
    seller = models.ForeignKey(Consumer, related_name='seller')
    buyer = models.ForeignKey(Consumer, related_name='buyer')
    total_amount_of_transaction = models.FloatField()
    total_paid = models.FloatField()
    total_due = models.FloatField()
    last_paid_amount = models.FloatField()
    last_date_of_payment = models.DateTimeField(auto_now=True, auto_now_add=False)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.seller


class Transaction(models.Model):
    callID = models.ForeignKey(VoiceRecord, related_name='transaction_which_call', null=True, blank=True)
    seller = models.ForeignKey(Consumer, related_name='seller_transaction')
    buyer = models.ForeignKey(Consumer, related_name='buyer_transaction')
    total_amount = models.FloatField()
    transcriber = models.ForeignKey(Transcriber, related_name='who_did_this_transaction', null=True, blank=True)
    total_paid = models.FloatField()
    total_due = models.FloatField()
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.id


class dueTransaction(models.Model):
    seller = models.ForeignKey(Consumer, related_name='seller_due_transaction')
    buyer = models.ForeignKey(Consumer, related_name='buyer_due_transaction')
    total_amount = models.FloatField()
    total_paid = models.FloatField()
    total_due = models.FloatField()
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.id


class ProductsInTransaction(models.Model):
    TID = models.ForeignKey(Transaction)
    product = models.ForeignKey(Product)
    unit = models.CharField(max_length=32)
    price_per_unit = models.FloatField()
    quantity = models.FloatField()
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.id
