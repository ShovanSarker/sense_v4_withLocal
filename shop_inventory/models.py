from django.db import models
from subscriber.models import Consumer
from product.models import Product
# Create your models here.


class Inventory(models.Model):
    shop = models.ForeignKey(Consumer, related_name='shop')
    product = models.ForeignKey(Product)
    unit = models.CharField(max_length=32)
    left = models.FloatField()
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.shop


class ProductInventory(models.Model):
    product = models.ForeignKey(Product, related_name='how_many_sold')
    unit = models.CharField(max_length=32)
    sold = models.FloatField()
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.shop


class BuySellProfitInventory(models.Model):
    shop = models.ForeignKey(Consumer, related_name='shop_whos_profit_calculating')
    product = models.ForeignKey(Product)
    unit = models.CharField(max_length=32)
    buying_price = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.shop


class BuySellProfitInventoryIndividual(models.Model):
    shop = models.ForeignKey(Consumer, related_name='shop_whos_profit_calculating_for_a_transaction')
    product = models.ForeignKey(Product, related_name='profit_calculating_for_a_transaction')
    unit = models.CharField(max_length=32)
    buying_price = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.shop


class ProductBuySellProfitInventory(models.Model):
    product = models.ForeignKey(Product, default='profit_of_which_product')
    unit = models.CharField(max_length=32)
    buying_price = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    total_sold = models.FloatField(default=0)
    q_profit = models.FloatField(default=0)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.product
